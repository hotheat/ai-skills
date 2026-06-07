# 归属说明

本文档记录本仓库中各个 skill 的来源、启发和改写历史。

## 约定

- `Original`: 从零创建。
- `Inspired`: 受到某个想法、结构、文章或外部参考启发，但已重新编写。
- `Adapted`: 基于已有 skill 或内部文档改写，并做了实质性调整。
- `Forked`: 基本沿用另一个 skill，仅做少量修改。

## Skills

### personal/agents-md-onboard

- 状态: Inspired
- 启发来源:
  - [HumanLayer - Writing a good CLAUDE.md](https://www.humanlayer.dev/blog/writing-a-good-claude-md)
  - 用户提供的 AGENTS.md 生成规则和 progressive disclosure 要求。
- 改写说明:
  - 将 HumanLayer 文章中关于 `CLAUDE.md` 的代码库 onboarding、少即是多、WHAT/WHY/HOW、progressive disclosure 和文件引用原则，改写为适配 Codex 的 `AGENTS.md` 生成流程。
  - 新建为 Codex skill，用于分析仓库并生成短根 `AGENTS.md` 与 `.codex/docs/architectural_patterns.md`。
  - 约束根文档少于 150 行，使用文件行号证据，并把专项内容拆到 `.codex/docs/`。

### personal/bilibili-render-pdf

- 状态: Adapted
- 启发来源:
  - [wdkns/wdkns-skills `skills/bilibili-render-pdf`](https://github.com/wdkns/wdkns-skills/tree/main/skills/bilibili-render-pdf)
- 差异化说明:
  - 在上游 Bilibili 课程笔记和 PDF 生成流程基础上，加入 remote ASR 优先级：CC 字幕后先尝试 `.env` 中的 `ASR_SERVICE_URL`，再回退到本地 Whisper，最后进入 visual-only 模式。
  - 增加 `scripts/transcribe_audio.py`，封装 remote SRT、remote JSON segments 转 SRT、本地 Whisper fallback 和 ASR 结果元数据输出。
  - 增加按 BV 号创建隔离工作目录的强制流程，避免多视频并发时覆盖 `audio.wav`、字幕、frames、`notes.tex` 或 PDF 产物。
  - 强化长视频处理为 outline + 1-2 个分P或 15-20 分钟窗口的分段写作流程，并要求整合时去重、补过渡和统一最终叙事。
  - 保留并本地化 `assets/notes-template.tex`，要求封面图、关键帧、教学框、总结与延伸共同进入最终可编译 PDF。

### personal/brainstorming

- 状态: Forked
- 启发来源:
  - [obra/superpowers `skills/brainstorming`](https://github.com/obra/superpowers/tree/main/skills/brainstorming)
- 改写说明:
  - 基本沿用原始 brainstorming skill 的协作式需求澄清、设计确认和 spec 产出流程。
  - 将 description 改为手动触发限定，避免普通功能、设计或实现请求自动加载该 skill。
  - 调整为 Codex skill 目录结构和仓库归属记录。

### personal/clean-git-branches

- 状态: Original
- 启发来源:
  - 用户对本地和远程 Git stale branches、已合并 PR 分支、缺失 tracking 分支、按保留周期清理分支的安全自动化需求。
- 改写说明:
  - 新建为 Codex skill，用于安全清理 Git 本地分支和远程分支。
  - 保留 dry-run 优先、受保护分支跳过、merged PR 检测、remote-missing 检测、按月龄清理和中文交互确认。
  - 调整为本仓库 `personal/` skill 目录结构和归属记录。

### personal/clash-verge-proxy-manager

- 状态: Original
- 启发来源:
  - 用户对 macOS Clash Verge Rev、MyProxy/MyLocal、白名单代理规则、默认 DIRECT 路由和运行时验证的维护需求。
- 改写说明:
  - 新建为 Codex skill，用于维护 Clash Verge Rev 的代理配置、规则插入、热重载和运行时验证。
  - 保留 `scripts/add_rules.rb` 作为规则插入 helper，并在迁移到仓库时将本机路径改为 `$HOME` 形式、将代理凭据改为占位符。
  - 调整为本仓库 `personal/` skill 目录结构和归属记录。

### personal/executing-plans

- 状态: Forked
- 启发来源:
  - [obra/superpowers `skills/executing-plans/SKILL.md`](https://github.com/obra/superpowers/blob/main/skills/executing-plans/SKILL.md?plain=1)
- 改写说明:
  - 基本沿用原始 executing-plans skill 的计划读取、批判性审阅、任务执行、验证和阻塞时停止询问流程。
  - 调整为 Codex skill 目录结构和仓库归属记录。

### personal/export-flomo-to-obsidian

- 状态: Original
- 启发来源:
  - 用户对 Flomo 导出包迁移到 Obsidian vault 的工作流需求。
- 改写说明:
  - 新建为 Codex skill，用于把 Flomo zip 导出为 Obsidian Markdown notes。
  - 保留脚本化导入、frontmatter、标签、附件、幂等 key、相关笔记 wikilink 和 vault 内文件嵌入处理。
  - 调整为本仓库 `personal/` skill 目录结构和归属记录。

### personal/nest-best-practices

- 状态: Inspired
- 启发来源:
  - 用户确认的 Nest clean architecture 原则：UseCase、Service、Port、Adapter、Controller、DI token、composition root、runtime config 和边界测试。
  - [hotheat/typescript-clean](https://github.com/hotheat/typescript-clean)
  - 本地 `react-best-practices` skill 的 progressive disclosure 结构。
- 改写说明:
  - 新建为 Codex skill，用于设计、重构和审查 NestJS 后端。
  - 将规则拆成 `SKILL.md` 和 `rules/`，覆盖项目形态、UseCase/Port/Adapter、DI/config、cross-cutting/async、测试与交付。
  - 调整为本仓库 `personal/` skill 目录结构和归属记录。

### personal/planner

- 状态: Inspired
- 启发来源:
  - [affaan-m/ECC `agents/planner.md`](https://github.com/affaan-m/ECC/blob/main/agents/planner.md)
- 改写说明:
  - 基于本地已整理的 planner skill 加入本仓库。
  - 保留规划专家、需求分析、架构审查、阶段拆解、测试策略、风险识别和成功标准等核心工作流。
  - 调整为 Codex skill 目录结构和仓库归属记录。

### personal/pptd-template-pipeline

- 状态: Inspired
- 启发来源:
  - Kimi PPT agent 中根据模板和输入内容从头生成 PPT 的工作流。
- 改写说明:
  - 改写为 Codex skill，用于基于 PPTD 的模板解析、内容规划、幻灯片生成、检查器修复循环和最终验证。
  - 启发过程通过 Codex Computer Use 整理。

### personal/ppt-template-style-reflow

- 状态: Inspired
- 启发来源:
  - Kimi PPT agent 中输入模板文件和对应内容 PPT 文件，并将模板风格复刻到内容 PPT 上的工作流。
- 改写说明:
  - 改写为 Codex skill，用于 PPTD 转换、模板风格提取、内容 PPT 重排、验证、导出和视觉 QA。
  - 启发过程通过 Codex Computer Use 整理。

### personal/react-best-practices

- 状态: Inspired
- 启发来源:
  - [flpbalada/my-opencode-config `project-structure`](https://skills.sh/flpbalada/my-opencode-config/project-structure)
  - [trsoliu/react-best-practices `react-best-practices`](https://skills.sh/trsoliu/react-best-practices/react-best-practices)
  - 用户确认的对比结论：`project-structure` 更简短、更聚焦，强项是 feature-based 架构、单向依赖、文件落位决策和反模式规避；`react-best-practices` 更适合现有项目演进，覆盖 SPA 技术栈、Tailwind/Bulma 迁移、表单、数据流、测试与交付。
  - 最终吸纳到本 skill 的内容包括：单向依赖原则、代码存放位置决策表、反模式清单、可选的 import restriction 执行建议。
  - 项目级硬性规则需要同步写入 `AGENTS.md` 或 `CLAUDE.md`，包括 pages 薄化、feature 边界划分、禁止跨 feature 导入、禁止使用 `src/lib`、表单、Hook 和性能相关规则；ESLint import restriction 不作为默认方案，因为当前项目主 lint 基线是 Biome。
- 改写说明:
  - 新建为 Codex skill，用于创建、重构、扩展或审查 React SPA 前端。
  - 将规则拆成 `SKILL.md` 和 `rules/`，覆盖技术栈选择、单应用架构、UI 系统、状态/表单/数据流、测试与交付。
  - 调整为本仓库 `personal/` skill 目录结构和归属记录。

### personal/receiving-code-review

- 状态: Inspired
- 启发来源:
  - [obra/superpowers `skills/receiving-code-review`](https://github.com/obra/superpowers/tree/main/skills/receiving-code-review)
- 改写说明:
  - 基于本地已整理的 receiving-code-review skill 加入本仓库。
  - 保留“先理解、再验证、再判断是否实施”的代码审查反馈处理流程。
  - 调整为 Codex skill 目录结构和仓库归属记录。

### personal/requesting-code-review

- 状态: Inspired
- 启发来源:
  - [obra/superpowers `skills/requesting-code-review`](https://github.com/obra/superpowers/tree/main/skills/requesting-code-review)
- 改写说明:
  - 基于本地已整理的 requesting-code-review skill 加入本仓库。
  - 保留基于 git range、审查上下文模板、严重级别分类和反馈处理的代码审查请求流程。
  - 调整为 Codex skill 目录结构和仓库归属记录。

### personal/systematic-debugging

- 状态: Inspired
- 启发来源:
  - [obra/superpowers `skills/systematic-debugging`](https://github.com/obra/superpowers/tree/main/skills/systematic-debugging)
- 改写说明:
  - 基于本地已整理的 systematic-debugging skill 加入本仓库。
  - 保留先定位根因、再提出修复、再补防御式验证的系统调试流程。
  - 排除创建日志和压力测试材料，仅保留运行 skill 所需的核心说明、参考文件和脚本。
  - 调整为 Codex skill 目录结构和仓库归属记录。

### personal/test-driven-development

- 状态: Inspired
- 启发来源:
  - [obra/superpowers `skills/test-driven-development`](https://github.com/obra/superpowers/tree/main/skills/test-driven-development)
- 改写说明:
  - 基于本地已整理的 test-driven-development skill 加入本仓库。
  - 保留 red-green-refactor、先写失败测试、最小实现和测试反模式检查流程。
  - 调整为 Codex skill 目录结构和仓库归属记录。

### personal/verification-before-completion

- 状态: Forked
- 启发来源:
  - [obra/superpowers `skills/verification-before-completion/SKILL.md`](https://github.com/obra/superpowers/blob/main/skills/verification-before-completion/SKILL.md)
- 改写说明:
  - 基本沿用原始 verification-before-completion skill 的 evidence before claims、完成前必须运行验证、读取完整输出、再声明状态的流程。
  - 调整为 Codex skill 目录结构和仓库归属记录。

### deep-understanding

- 状态: Inspired
- 启发来源:
  - [ThariqS - Deep Understanding Prompt](https://gist.github.com/ThariqS/1389dcdff9eba4789887a2211370f06b)
- 改写说明:
  - 基于原始 prompt 改写为 Codex skill 格式。
  - 保留增量式教学验证、理解清单、互动问答（ELI5/ELI14/ELII）和测验等核心流程。
  - 调整为 Codex skill 目录结构和仓库归属记录。
