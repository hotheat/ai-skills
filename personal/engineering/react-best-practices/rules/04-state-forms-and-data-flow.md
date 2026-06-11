## 状态、表单与数据流

### 状态边界

- Global state
  - 只放跨路由、跨 feature 的长期状态，例如 auth/session
- Server state
  - 优先用 TanStack Query 管理
- Feature-local transient state
  - 拖拽状态、局部 modal、上传选择、临时编辑态、轮询中间态
  - 不要为了“统一”而塞进全局 store

### 数据流

默认采用这条链路：

1. `src/utils/api_client.ts` 暴露底层客户端或 HTTP helper
2. `src/features/<feature>/api.ts` 做 feature 级解包和接口封装
3. `src/features/<feature>/hooks/*` 做 query、mutation、polling、view-model
4. `screen` 组合 hooks，组织页面骨架
5. `components` 只渲染 props

补充约束：

- 页面不要直接消费底层 API client
- 不要在多个页面里重复写同一套解包逻辑
- 不要为了共享数据而让 feature 之间直接互相 import hooks 或 query 实现

### 表单规则

- 简单上传、单按钮动作、局部配置切换
  - 优先本地 state
- 多字段输入、校验、错误映射、后端返回字段错误
  - 优先 `React Hook Form + Zod`

### 导出规则

- `src/pages/*`
  - 允许 `default export`
- `src/features/*`、`src/components/*`、`src/utils/*`
  - 默认使用命名导出

### Hook 抽取规则

- 同类流程在 2 个页面出现，就抽
- 一个 screen 同时承担“请求 + 轮询 + 视图派生 + 大段 JSX”，就拆
- Hook 优先抽“流程”和“view-model”，不是抽零碎的 setter
- 若多个 feature 需要相同流程，优先抽到共享 workflow，而不是相互引用对方 hook

### 性能规则

- 不追求到处使用 `useMemo` / `useCallback`
- 只在这些场景使用：
  - 派生计算确实重
  - 稳定引用能减少子组件无意义重渲染
  - effect 或 callback 依赖确实需要稳定
- 不要为了“看起来专业”而机械加 memo

### Query 组织规则

- 查询 key 尽量按 feature 聚合
- DTO 解包和字段兜底优先放 `api.ts` 或 mapper
- 页面不要到处写 `res.data.data`
