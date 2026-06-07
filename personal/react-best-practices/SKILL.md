---
name: react-best-practices
description: "React 单应用与中型 SPA 架构规范（中文）。用于创建、重构、扩展或审查基于 React 18/19 + TypeScript + Vite + React Router + Zustand + TanStack Query + Tailwind 的前端，尤其适合把 page-heavy 代码演进为 feature-based 结构、建立 pages/features/components/ui/shared/utils 边界、规范表单与数据流、或将 Bulma/Bootstrap 等遗留页面迁移到 Tailwind-first 组件系统。"
---

# React SPA Best Practices

默认把这类项目视为“React 单应用中型项目”，而不是 monorepo 模板。

## 默认立场

- 先检查仓库现状，再给结构建议；不要把别处的模板直接套到当前项目上。
- 单应用 React SPA 默认优先于 monorepo。只有仓库已经是 monorepo，或用户明确需要多应用/多包时，才往 `apps/*`、`packages/*` 方向扩展。
- 保留仓库已有包管理器、lint、测试和构建约定；不要强推 `pnpm`、`turbo`、`changesets`、`ESLint + Prettier`。
- 若仓库已有成熟设计系统，优先延续；若没有或正处于遗留页面迁移期，默认采用 `Tailwind-first + shared UI primitives`。
- 默认把 `src/pages/*` 视为路由适配层，把业务实现放进 `src/features/*`。
- 保留 `src/utils/*` 作为通用工具与集成层；不要引入宽泛的 `src/lib` 垃圾抽屉。
- 默认采用单向依赖：`utils/components/ui -> components/shared/features -> app/pages`；不要跨 feature 互相引用实现。

## 使用流程

1. 先检查项目的真实约束：
   - 包管理器、脚本、lint、test、build 命令
   - 路由入口、providers、状态管理、样式入口
   - 是否已有设计系统或遗留 UI 框架
2. 根据项目类型选择结构：
   - 单应用 React SPA：读取 `rules/02-single-spa-architecture.md`
   - 需要 UI 重构或遗留样式迁移：读取 `rules/03-ui-system.md`
   - 需要规范状态、表单、hooks、导出、性能：读取 `rules/04-state-forms-and-data-flow.md`
   - 需要补测试、review 或交付约束：读取 `rules/05-testing-review-and-delivery.md`
3. 设计或实现时坚持这些默认规则：
   - `src/pages/*` 只负责路由入口、权限包装、参数转发
   - `src/features/<feature>/*` 承接 screen、hooks、api、components、types、schema
   - `src/components/ui/*` 放共享 UI 原语
   - `src/components/shared/*` 放跨 feature 复用组合组件
   - `src/features/*/components/*` 放 feature 内部组件
4. 遇到这些情况时主动调整抽象层次：
   - 同类流程在 2 个页面出现：抽 hook 或 shared workflow
   - 一个 screen 同时承担请求、轮询、视图派生和大段 JSX：拆 screen、hook、presentational components
   - 多字段、校验、错误映射：用 `React Hook Form + Zod`
   - 简单上传、单按钮动作：优先本地 React state
5. 做代码审查或重构时，优先找：
   - route file 过重
   - feature-local 组件被错误放进 shared
   - feature 之间直接互相 import
   - API client 在页面里到处散落
   - Bulma/Bootstrap 遗留 class 在新组件继续扩张
   - 无必要的 `useMemo` / `useCallback`

## 何时不要照搬默认规则

- 仓库已经有明确且稳定的设计系统时，不要为了 Tailwind-first 再造一层体系。
- 仓库已经是 Next.js、Remix、monorepo 或 data-router 架构时，不要强行改回单应用 Vite SPA 模式。
- 仓库明确要求 `default export` 或文件布局另有团队规范时，先遵守仓库规范，再做局部优化。

## 参考文件

- `rules/01-tech-stack.md`
  - 何时使用这套 React SPA 技术栈，哪些工具是默认项，哪些是条件项
- `rules/02-single-spa-architecture.md`
  - 单应用 React 中型项目推荐目录结构、单向依赖和文件落位规则
- `rules/03-ui-system.md`
  - Tailwind-first UI 体系、遗留 Bulma/Bootstrap 迁移、图标和通知方案
- `rules/04-state-forms-and-data-flow.md`
  - 状态边界、数据流、表单策略、导出规则、Hook 抽取、性能约定
- `rules/05-testing-review-and-delivery.md`
  - 测试、代码审查、交付和 CI 的最小可执行标准
