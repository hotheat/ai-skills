## 单应用 React SPA 架构

默认推荐单应用结构，适用于大多数 React 18/19 + Vite + React Router 项目。

### 目录结构

```text
src/
  app/
    providers/
    router/
    layout/
    auth/
  pages/
    FooPage.tsx
  features/
    foo/
      screen/
      hooks/
      api.ts
      components/
      types.ts
      schema.ts
  components/
    ui/
    shared/
  hooks/
  stores/
  utils/
  styles/
```

### 边界规则

- `src/pages/*`
  - 只做路由入口、layout/auth 包装、route params 和 search params 转发
  - 默认允许 `default export`
- `src/features/<feature>/*`
  - 放这个 feature 的 screen、hooks、api、components、types、schema
  - 这里是业务实现主目录
- `src/components/ui/*`
  - 放共享 UI 原语和 `shadcn/ui` 包装层
- `src/components/shared/*`
  - 放跨 feature 复用的组合组件
- `src/features/<feature>/components/*`
  - 放 feature 专属组件
  - 不要过早塞进 `components/shared`
- `src/utils/*`
  - 放无业务语义的通用工具和集成能力
  - 不要引入宽泛的 `src/lib`

### 单向依赖规则

默认采用单向依赖，而不是任意跨目录引用：

```text
src/utils
src/components/ui
  -> src/components/shared
  -> src/features/*
  -> src/app and src/pages
```

约束：

- `src/features/*` 不要直接 import 其他 feature 的内部实现
- 如果两个 feature 需要共享代码，优先上提到：
  - `src/utils/*`
  - `src/components/ui/*`
  - `src/components/shared/*`
- `src/pages/*` 不要反向承载 feature 内部逻辑
- `src/app/*` 负责 providers、layout、router，不要吸收具体业务实现

### 文件落位决策表

| 场景 | 推荐位置 |
|------|----------|
| 路由入口、auth/layout 包装 | `src/pages/*` |
| 一个页面对应的主业务实现 | `src/features/<feature>/screen/*` |
| 只在一个 feature 内使用的组件 | `src/features/<feature>/components/*` |
| 跨 feature 复用的组合组件 | `src/components/shared/*` |
| Button/Dialog/Tabs/Input 等 UI 原语 | `src/components/ui/*` |
| feature 级 API 封装与 DTO 解包 | `src/features/<feature>/api.ts` |
| 通用工具、客户端封装、错误/日期/文件工具 | `src/utils/*` |
| 仅跨路由共享的长期状态 | `src/stores/*` |
| feature 内查询、mutation、polling、view-model | `src/features/<feature>/hooks/*` |

### 默认演进策略

- 新功能默认落在 `src/features/*`
- 老页面逐步薄化为 `pages -> feature screen`
- 共享抽象从“重复交互模式”开始抽，不从“重复 HTML 外形”开始抽

### 反模式

- 在 `src/pages/*` 里直接写完整业务实现
- `src/features/a/*` 直接引用 `src/features/b/*` 的内部组件或 hooks
- 把只服务一个 feature 的组件放进 `src/components/shared/*`
- 把业务逻辑塞进 `src/components/ui/*`
- 用 `src/lib` 充当无法归类内容的兜底目录

### 执行建议

若仓库使用 ESLint 或其他 import 规则系统，建议对目录边界做静态约束：

- 禁止跨 feature 深层 import
- 禁止 `src/features/*` 引用其他 feature 的内部路径
- 禁止 `src/components/ui/*` 依赖 feature 目录

如果仓库已有 Biome 但没有 import restriction 能力，可在现有 lint 之外补充最小 ESLint 规则，仅用于目录边界约束。

### 何时考虑 monorepo

只有满足以下条件之一时才推荐扩展为 monorepo：

- 已经存在多个前端应用
- 存在共享组件包、SDK 包、配置包的明确边界
- CI、发布、版本管理已经要求多包协作

否则，优先把单应用内部结构做好，而不是提早上 `apps/*`、`packages/*`。
