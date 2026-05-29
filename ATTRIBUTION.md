# 归属说明

本文档记录本仓库中各个 skill 的来源、启发和改写历史。

## 约定

- `Original`: 从零创建。
- `Inspired`: 受到某个想法、结构、文章或外部参考启发，但已重新编写。
- `Adapted`: 基于已有 skill 或内部文档改写，并做了实质性调整。
- `Forked`: 基本沿用另一个 skill，仅做少量修改。

## Skills

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
