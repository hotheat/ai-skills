## UI 与样式体系

### 默认选择

- 新项目或重构中的 React SPA，默认采用 `Tailwind-first`
- 共享 UI 原语默认采用 `shadcn/ui + Radix`
- 图标默认采用 `lucide-react`
- 通知默认采用 `sonner`

### 设计系统选择规则

- 仓库已有成熟设计系统：优先保留并延续
- 仓库只有 Bulma、Bootstrap、Ant Design 等遗留页面样式，且结构耦合严重：
  - 把旧框架视为迁移依赖，而不是长期目标
  - 新 screen 和新 shared components 不再继续写旧框架 class

### 遗留 UI 替换关系

- `navbar / tabs / dropdown / modal / progress / card / form`
  - 优先改成 `shadcn/ui` 组件
- `hero / columns / level / spacing / helpers / panel`
  - 优先改成 Tailwind 布局和 `src/components/shared/layout/*`
- `notification / toast`
  - 优先统一到 `sonner`
- `fontawesome / bootstrap icons / bulma icons`
  - 优先统一到 `lucide-react`

### 共享组件抽取顺序

先抽高重复交互，再抽纯展示外壳：

1. `PageHeader`
2. `AppShell` / `FeatureShell`
3. `UploadDropzone`
4. `SelectedFileCard` / `SelectedFileList`
5. `TaskStatusPanel`
6. `InlineNotice` / `ConfirmDialog`

### 不要做的事

- 不要让 `components/ui` 变成业务组件目录
- 不要在新组件里继续堆 Bulma/Bootstrap helper class
- 不要同时维护两套主样式体系而没有迁移边界
