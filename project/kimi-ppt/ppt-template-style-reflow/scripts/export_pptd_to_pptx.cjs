#!/usr/bin/env node
const fs = require("fs");
const path = require("path");

let pptxgen;
try {
  pptxgen = require("pptxgenjs");
} catch (error) {
  console.error("pptxgenjs is required for PPTX export. Install it or run inside the Codex primary runtime.");
  console.error(error.message);
  process.exit(2);
}

function parseArgs(argv) {
  const args = { pptd: null, output: null };
  for (let i = 2; i < argv.length; i++) {
    const arg = argv[i];
    if ((arg === "-o" || arg === "--output") && argv[i + 1]) {
      args.output = argv[++i];
    } else if (!args.pptd) {
      args.pptd = arg;
    } else {
      throw new Error(`Unexpected argument: ${arg}`);
    }
  }
  if (!args.pptd) throw new Error("Usage: export.sh <deck.pptd> -o <deck.pptx>");
  if (!args.output) args.output = args.pptd.replace(/\.pptd$/i, ".pptx");
  return args;
}

function stripQuotes(value) {
  value = String(value || "").trim();
  if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
    return value.slice(1, -1);
  }
  return value;
}

function parseSize(text) {
  const m = text.match(/^\s*size:\s*\[([^\]]+)\]/m);
  if (!m) return [1280, 720];
  return m[1].split(",").slice(0, 2).map((v) => Number(v.trim()));
}

function parsePages(text) {
  const pages = [];
  let inPages = false;
  for (const line of text.split(/\r?\n/)) {
    if (/^\s*pages:\s*$/.test(line)) {
      inPages = true;
      continue;
    }
    if (inPages) {
      const m = line.match(/^\s*-\s+(.+?)\s*$/);
      if (m) pages.push(stripQuotes(m[1]));
      else if (line && !/^\s/.test(line)) inPages = false;
    }
  }
  return pages;
}

function parseBounds(value) {
  const m = String(value).match(/\[([^\]]+)\]/);
  if (!m) return null;
  return m[1].split(",").slice(0, 4).map((v) => Number(v.trim()));
}

function parsePage(file) {
  const lines = fs.readFileSync(file, "utf8").split(/\r?\n/);
  const elements = [];
  let current = null;
  let context = "";
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    let m = line.match(/^\s*-\s+elementId:\s*(.+?)\s*$/);
    if (m) {
      current = { elementId: stripQuotes(m[1]) };
      elements.push(current);
      context = "";
      continue;
    }
    if (!current) continue;
    if ((m = line.match(/^\s*elementType:\s*(.+?)\s*$/))) {
      current.elementType = stripQuotes(m[1]);
      context = "";
    } else if ((m = line.match(/^\s*bounds:\s*(.+?)\s*$/))) {
      current.bounds = parseBounds(m[1]);
      context = "";
    } else if ((m = line.match(/^\s*src:\s*(.+?)\s*$/))) {
      current.src = stripQuotes(m[1]);
      context = "";
    } else if ((m = line.match(/^\s*opacity:\s*([0-9.]+)/))) {
      current.opacity = Number(m[1]);
    } else if (/^\s*fill:\s*$/.test(line)) {
      context = "fill";
    } else if (/^\s*content:\s*$/.test(line)) {
      context = "content";
    } else if ((m = line.match(/^\s*color:\s*(.+?)\s*$/))) {
      current[context === "content" ? "contentColor" : "fillColor"] = stripQuotes(m[1]);
    } else if ((m = line.match(/^\s*fontSize:\s*([0-9.]+)/))) {
      current.fontSize = Number(m[1]);
    } else if ((m = line.match(/^\s*fontFamily:\s*(.+?)\s*$/))) {
      current.fontFamily = stripQuotes(m[1]);
    } else if ((m = line.match(/^\s*align:\s*\[([^\]]+)\]/))) {
      current.align = m[1].split(",").map((v) => v.trim());
    } else if (/^\s*text:\s*\|\s*$/.test(line)) {
      const indent = line.length - line.trimStart().length;
      const textLines = [];
      i++;
      while (i < lines.length) {
        const next = lines[i];
        const nextIndent = next.length - next.trimStart().length;
        if (next.trim() && nextIndent <= indent) {
          i--;
          break;
        }
        textLines.push(next.length >= indent + 2 ? next.slice(indent + 2) : "");
        i++;
      }
      current.text = textLines.join("\n");
    }
  }
  return elements;
}

function stripHtml(html) {
  return String(html || "")
    .replace(/<\/p>\s*<p>/g, "\n")
    .replace(/<br\s*\/?>/g, "\n")
    .replace(/<[^>]+>/g, "")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&amp;/g, "&")
    .trim();
}

function normalizeColor(color, fallback) {
  color = String(color || fallback || "000000").trim();
  if (color.startsWith("#")) color = color.slice(1);
  if (/^[0-9a-fA-F]{6}$/.test(color)) return color.toUpperCase();
  return String(fallback || "000000").replace(/^#/, "");
}

function fit(value) {
  return Number(value || 0) / 96;
}

function resolveSrc(projectDir, src) {
  if (!src) return null;
  if (path.isAbsolute(src)) return src;
  return path.join(projectDir, src);
}

async function main() {
  const args = parseArgs(process.argv);
  const pptd = path.resolve(args.pptd);
  const output = path.resolve(args.output);
  const projectDir = path.dirname(pptd);
  const text = fs.readFileSync(pptd, "utf8");
  const [width, height] = parseSize(text);
  const pages = parsePages(text);

  const pptx = new pptxgen();
  pptx.author = "ppt-template-style-reflow";
  pptx.subject = "Exported from PPTD-like project";
  pptx.title = path.basename(output, ".pptx");
  pptx.company = "OpenAI Codex";
  pptx.defineLayout({ name: "PPTD_CUSTOM", width: fit(width), height: fit(height) });
  pptx.layout = "PPTD_CUSTOM";

  for (const pageRef of pages) {
    const slide = pptx.addSlide();
    slide.background = { color: "FFFFFF" };
    const pageFile = path.join(projectDir, pageRef);
    const elements = fs.existsSync(pageFile) ? parsePage(pageFile) : [];
    for (const el of elements) {
      const b = el.bounds || [0, 0, 0, 0];
      const common = { x: fit(b[0]), y: fit(b[1]), w: fit(b[2]), h: fit(b[3]) };
      if (el.elementType === "shape") {
        const fill = normalizeColor(el.fillColor, "FFFFFF");
        const shape = String(el.shapeName || "").includes("ellipse") ? pptx.ShapeType.ellipse : pptx.ShapeType.rect;
        slide.addShape(shape, { ...common, fill: { color: fill, transparency: el.opacity != null ? Math.round((1 - el.opacity) * 100) : 0 }, line: { color: fill, transparency: 100 } });
      } else if (el.elementType === "image") {
        const imagePath = resolveSrc(projectDir, el.src);
        if (imagePath && fs.existsSync(imagePath)) {
          slide.addImage({ path: imagePath, ...common, transparency: el.opacity != null ? Math.round((1 - el.opacity) * 100) : 0 });
        }
      } else if (el.elementType === "text") {
        const raw = String(el.text || "");
        const align = el.align || ["left", "top"];
        slide.addText(stripHtml(raw), {
          ...common,
          margin: 0.04,
          fontFace: String(el.fontFamily || "Arial").split(",")[0],
          fontSize: Number(el.fontSize || 18),
          color: normalizeColor(el.contentColor, "111111"),
          bold: /<(strong|b)>/i.test(raw),
          align: align[0] === "center" ? "center" : align[0] === "right" ? "right" : "left",
          valign: align[1] === "middle" ? "mid" : align[1] === "bottom" ? "bottom" : "top",
          fit: "shrink",
        });
      }
    }
  }

  fs.mkdirSync(path.dirname(output), { recursive: true });
  await pptx.writeFile({ fileName: output });
  console.log(`Created: ${output}`);
}

main().catch((error) => {
  console.error(error.stack || error.message || String(error));
  process.exit(1);
});
