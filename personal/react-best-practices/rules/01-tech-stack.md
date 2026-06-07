## 技术栈基线

适合这份 skill 的默认项目画像：

- React 18/19
- TypeScript 严格模式
- Vite
- React Router
- TanStack Query
- Zustand
- Tailwind CSS

### 默认推荐项

| 领域 | 默认选择 | 备注 |
|------|----------|------|
| 语言 | TypeScript | 建议开启 strict |
| UI 框架 | React 18/19 | |
| 构建 | Vite | 单应用 React SPA 默认优先 |
| 路由 | React Router | |
| 服务端状态 | TanStack Query | |
| 全局客户端状态 | Zustand | 仅用于真正跨 feature 的长期状态 |
| 样式 | Tailwind-first | 保留已有设计系统时例外 |
| UI 原语 | shadcn/ui + Radix | 有利于中型项目组件分层 |
| 表单 | React Hook Form + Zod | 仅用于多字段、可校验表单 |
| 图标 | lucide-react | |
| 通知 | sonner | |

### 条件项

- `Vitest + Testing Library`
  - 仓库已有或用户要求时优先
- `Playwright`
  - 关键用户路径复杂、需要浏览器级回归时引入
- `Axios / ky`
  - 若仓库没有生成客户端，或需要统一 HTTP 封装时采用
- `pnpm / Turborepo / Changesets`
  - 仅在仓库本来就是 monorepo 或明确需要多包治理时采用

### 不要预设的事

- 不要默认认为所有 React 项目都该用 monorepo
- 不要默认把 `ESLint + Prettier` 强加给已经使用 Biome 或其他工具的仓库
- 不要把“企业级模板”当成所有 React 项目的最佳起点
