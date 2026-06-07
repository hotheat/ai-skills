# 归属说明

本文档记录本仓库中各个 skill 的来源、启发和改写历史。

## 约定

- `Original`: 从零创建。
- `Inspired`: 受到某个想法、结构、文章或外部参考启发，但已重新编写。
- `Adapted`: 基于已有 skill 或内部文档改写，并做了实质性调整。
- `Forked`: 基本沿用另一个 skill，仅做少量修改。

## Skills

### personal/agents-md-onboard

- 状态: Original
- 启发来源:
  - 用户提供的 AGENTS.md 生成规则和 progressive disclosure 要求。
- 改写说明:
  - 新建为 Codex skill，用于分析仓库并生成短根 `AGENTS.md` 与 `.codex/docs/architectural_patterns.md`。
  - 约束根文档少于 150 行，使用文件行号证据，并把专项内容拆到 `.codex/docs/`。

### personal/brainstorming

- 状态: Forked
- 启发来源:
  - [obra/superpowers `skills/brainstorming`](https://github.com/obra/superpowers/tree/main/skills/brainstorming)
- 改写说明:
  - 基本沿用原始 brainstorming skill 的协作式需求澄清、设计确认和 spec 产出流程。
  - 将 description 改为手动触发限定，避免普通功能、设计或实现请求自动加载该 skill。
  - 调整为 Codex skill 目录结构和仓库归属记录。

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

### deep-understanding

- 状态: Inspired
- 启发来源:
  - [ThariqS - Deep Understanding Prompt](https://gist.github.com/ThariqS/1389dcdff9eba4789887a2211370f06b)
- 改写说明:
  - 基于原始 prompt 改写为 Codex skill 格式。
  - 保留增量式教学验证、理解清单、互动问答（ELI5/ELI14/ELII）和测验等核心流程。
  - 调整为 Codex skill 目录结构和仓库归属记录。
