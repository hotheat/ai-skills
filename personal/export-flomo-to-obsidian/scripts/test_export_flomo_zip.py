#!/usr/bin/env python3

import base64
import os
import pathlib
import tempfile
import textwrap
import unittest
import zipfile
from unittest import mock

from export_flomo_zip import export_zip


PNG_PIXEL = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wqz1fQAAAAASUVORK5CYII="
)


def make_sample_zip(zip_path: pathlib.Path) -> None:
    html = textwrap.dedent(
        """
        <html>
          <body>
            <div class="memos">
              <div class="memo">
                <div class="time">2026-04-13 11:54:56</div>
                <div class="content">
                  <p>Hermes 的记忆系统分了四层。</p>
                  <p>技能文件和上下文分层这个点很重要。</p>
                  <p>ObsidianFile：llm_wiki_summary.pdf</p>
                  <p>#Hermes/记忆系统</p>
                </div>
                <div class="files">
                  <img alt="memo image" src="file/2026-04-13/2169862/alpha.png" />
                </div>
              </div>
              <div class="memo">
                <div class="time">2026-04-13 12:00:00</div>
                <div class="content">
                  <p>Agent 的 Harness 决定了模型能不能投入生产。</p>
                  <p>这里也提到技能文件是分层记忆的一部分。</p>
                  <p>#Hermes/记忆系统</p>
                </div>
                <div class="files"></div>
              </div>
              <div class="memo">
                <div class="time">2026-04-13 12:30:00</div>
                <div class="content">
                  <p>今天去散步，顺便买了咖啡，也记下 #生活/散步 这个话题。</p>
                </div>
                <div class="files"></div>
              </div>
              <div class="memo">
                <div class="time">2026-04-13 12:45:00</div>
                <div class="content">
                  <p>这是一个很短的记录，只是提到上线提醒。</p>
                  <p>#Hermes/记忆系统</p>
                </div>
                <div class="files"></div>
              </div>
              <div class="memo">
                <div class="time">2026-04-14 08:00:00</div>
                <div class="content">
                  <p>手绘风信息图提示词。</p>
                  <p>#提示词/视觉</p>
                </div>
                <div class="files"></div>
              </div>
            </div>
          </body>
        </html>
        """
    ).strip()

    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("sample/我的笔记.html", html)
        archive.writestr("sample/file/2026-04-13/2169862/alpha.png", PNG_PIXEL)


def make_llm_fallback_zip(zip_path: pathlib.Path) -> None:
    html = textwrap.dedent(
        """
        <html>
          <body>
            <div class="memos">
              <div class="memo">
                <div class="time">2026-04-13 09:00:00</div>
                <div class="content">
                  <p>Juchats</p>
                  <p>这是一个围绕 LangGraph、MCP 和评测体系的项目速记，包含多代理运行时设计。</p>
                  <p>#测试/短标题</p>
                </div>
                <div class="files"></div>
              </div>
              <div class="memo">
                <div class="time">2026-04-13 09:05:00</div>
                <div class="content">
                  <p>https://example.com/agent-runtime</p>
                  <p>#测试/失败标题</p>
                </div>
                <div class="files"></div>
              </div>
              <div class="memo">
                <div class="time">2026-04-14 08:00:00</div>
                <div class="content">
                  <p>手绘风信息图提示词。</p>
                  <p>#提示词/视觉</p>
                </div>
                <div class="files"></div>
              </div>
            </div>
          </body>
        </html>
        """
    ).strip()

    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("sample/llm-fallback.html", html)


class ExportFlomoZipTests(unittest.TestCase):
    def test_export_requires_obsidian_vault_and_renders_obsidian_file_embeds(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = pathlib.Path(tmpdir)
            zip_path = tmp_path / "sample.zip"
            output_dir = tmp_path / "vault" / "flomo-import"
            vault_root = tmp_path / "vault"
            (vault_root / ".obsidian").mkdir(parents=True)
            (vault_root / "references").mkdir()
            (vault_root / "references" / "llm_wiki_summary.pdf").write_bytes(b"%PDF-1.4\n")
            make_sample_zip(zip_path)

            old_cwd = os.getcwd()
            os.chdir(vault_root)
            try:
                first = export_zip(zip_path, output_dir, related_limit=3, title_mode="heuristic")
                second = export_zip(zip_path, output_dir, related_limit=3, title_mode="heuristic")
            finally:
                os.chdir(old_cwd)

            self.assertEqual(first["created"], 5)
            self.assertEqual(first["skipped"], 0)
            self.assertEqual(second["created"], 0)
            self.assertEqual(second["skipped"], 5)

            note_paths = sorted(path for path in output_dir.rglob("*.md"))
            self.assertEqual(len(note_paths), 5)
            self.assertEqual({path.parent.name for path in note_paths}, {"2026-04-13", "2026-04-14"})
            self.assertTrue((output_dir / "2026-04-14" / "手绘风信息图提示词.md").exists())

            attachments_dir = output_dir / "attachments"
            attachment_paths = sorted(attachments_dir.glob("*"))
            self.assertEqual(len(attachment_paths), 1)

            hermes_notes = []
            coffee_note = None
            short_hermes_note = None
            prompt_note = None
            for note_path in note_paths:
                content = note_path.read_text(encoding="utf-8")
                self.assertIn("flomo_idempotency_key:", content)
                if "Hermes 的记忆系统分了四层。" in content:
                    hermes_notes.append((note_path, content))
                    self.assertEqual(note_path.parent.name, "2026-04-13")
                    self.assertEqual(note_path.name, "Hermes 的记忆系统分了四层.md")
                    self.assertIn("tags:", content)
                    self.assertIn("- Hermes/记忆系统", content)
                    self.assertIn("![[llm_wiki_summary.pdf]]", content)
                    self.assertIn("![[attachments/", content)
                    self.assertNotIn("ObsidianFile：llm_wiki_summary.pdf", content)
                elif "Agent 的 Harness 决定了模型能不能投入生产。" in content:
                    hermes_notes.append((note_path, content))
                    self.assertEqual(note_path.parent.name, "2026-04-13")
                elif "今天去散步，顺便买了咖啡，也记下 #生活/散步 这个话题。" in content:
                    coffee_note = (note_path, content)
                    self.assertEqual(note_path.parent.name, "2026-04-13")
                    self.assertIn("tags: []", content)
                elif "这是一个很短的记录，只是提到上线提醒。" in content:
                    short_hermes_note = (note_path, content)
                    self.assertEqual(note_path.parent.name, "2026-04-13")
                    self.assertIn("- Hermes/记忆系统", content)
                elif "手绘风信息图提示词。" in content:
                    prompt_note = (note_path, content)
                    self.assertIn("created: 2026-04-14", content)
                    self.assertEqual(note_path.parent.name, "2026-04-14")
                    self.assertEqual(note_path.name, "手绘风信息图提示词.md")
                    self.assertIn("- 提示词/视觉", content)

            self.assertEqual(len(hermes_notes), 2)
            self.assertIsNotNone(coffee_note)
            self.assertIsNotNone(short_hermes_note)
            self.assertIsNotNone(prompt_note)

            first_note_path, first_note = hermes_notes[0]
            second_note_path, second_note = hermes_notes[1]

            self.assertIn(
                f"[[{second_note_path.stem}]]: 共享标签 `Hermes/记忆系统`；共同短语 `技能文件`",
                first_note,
            )
            self.assertIn(
                f"[[{first_note_path.stem}]]: 共享标签 `Hermes/记忆系统`；共同短语 `技能文件`",
                second_note,
            )
            self.assertNotIn(f"[[{first_note_path.stem}]]", coffee_note[1])
            self.assertNotIn(f"[[{second_note_path.stem}]]", coffee_note[1])
            self.assertNotIn(f"[[{first_note_path.stem}]]", short_hermes_note[1])
            self.assertNotIn(f"[[{second_note_path.stem}]]", short_hermes_note[1])

    def test_export_fails_outside_obsidian_vault(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = pathlib.Path(tmpdir)
            zip_path = tmp_path / "sample.zip"
            output_dir = tmp_path / "output"
            make_sample_zip(zip_path)

            old_cwd = os.getcwd()
            os.chdir(tmp_path)
            try:
                with self.assertRaisesRegex(RuntimeError, "Current directory is not inside an Obsidian vault"):
                    export_zip(zip_path, output_dir, related_limit=3, title_mode="heuristic")
            finally:
                os.chdir(old_cwd)

    def test_export_uses_llm_only_for_short_or_generic_heuristic_titles(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = pathlib.Path(tmpdir)
            zip_path = tmp_path / "sample.zip"
            output_dir = tmp_path / "vault" / "flomo-import"
            vault_root = tmp_path / "vault"
            (vault_root / ".obsidian").mkdir(parents=True)
            make_llm_fallback_zip(zip_path)

            generator_calls: list[str] = []

            def fake_request_llm_title(source_text: str, model: str, api_key: str, base_url: str, timeout_seconds: float = 30.0) -> str:
                generator_calls.append(source_text)
                if "Juchats" in source_text:
                    return "Juchats 多代理运行时"
                if "https://example.com/agent-runtime" in source_text:
                    return "Agent Runtime 参考链接"
                raise AssertionError(f"unexpected LLM title request: {source_text}")

            old_cwd = os.getcwd()
            os.chdir(vault_root)
            try:
                with mock.patch.dict(
                    os.environ,
                    {
                        "FLOMO_TITLE_MODEL": "fake-title-model",
                        "FLOMO_TITLE_API_KEY": "fake-title-key",
                    },
                    clear=False,
                ):
                    with mock.patch("export_flomo_zip.request_llm_title", side_effect=fake_request_llm_title):
                        stats = export_zip(
                            zip_path,
                            output_dir,
                            related_limit=3,
                            title_mode="llm",
                        )
            finally:
                os.chdir(old_cwd)

            self.assertEqual(stats["created"], 3)
            self.assertTrue((output_dir / "2026-04-13" / "Juchats 多代理运行时.md").exists())
            self.assertTrue((output_dir / "2026-04-13" / "Agent Runtime 参考链接.md").exists())
            self.assertTrue((output_dir / "2026-04-14" / "手绘风信息图提示词.md").exists())
            self.assertEqual(len(generator_calls), 2)
            self.assertTrue(any("Juchats" in call for call in generator_calls))
            self.assertTrue(any("https://example.com/agent-runtime" in call for call in generator_calls))
            self.assertFalse(any("手绘风信息图提示词" in call for call in generator_calls))


if __name__ == "__main__":
    unittest.main()
