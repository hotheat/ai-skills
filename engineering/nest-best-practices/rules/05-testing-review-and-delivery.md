## 测试、Review 与交付

### 测试分层

- Core unit tests
  - 直接 `new Service(...)`
  - 使用 fake port / stub adapter
  - 覆盖 value object、entity、factory、use case
- Boundary tests
  - 禁止 core import `@nestjs/*`
  - 禁止 core service 使用 `@Injectable`、`@Inject`
  - 禁止 DI token 出现在 core
  - 检查 adapter implements port
- Module tests
  - 验证 Nest module 能解析 provider graph
  - 覆盖 token 绑定和 wrapper 装配
- Controller tests
  - 覆盖 payload 构造、HTTP exception、status mapping
  - 不重复测试 service 业务细节
- Adapter tests
  - 覆盖文件、DB、HTTP、queue、model SDK 的边界行为
- Prisma schema contract tests
  - 读取 `schema.prisma`，覆盖关键 model、relation、索引、字段映射和禁止出现的表/列
  - 修改 schema 后运行 Prisma format/generate/sync 命令；不要只靠 TypeScript 编译推断 schema 正确

### 最小验收

修改 backend 架构时，至少运行：

```bash
make lint
make test
```

若仓库没有 Makefile，使用实际 package scripts，例如：

```bash
pnpm typecheck
pnpm lint
pnpm test
```

涉及 build/runtime entry 时补：

```bash
pnpm build
```

### Review Checklist

先看事实：

- 当前 branch / diff / test command
- module provider graph
- controller -> use case 调用链
- service constructor dependencies
- port 和 adapter 文件位置
- `schema.prisma`、Prisma client factory、repository adapter 和 generate/push 命令
- config 是否 import-time 解析

重点找：

- Controller 直接依赖 concrete service
- Service 直接 import adapter
- core 依赖 Nest decorator
- core 或 shared 直接 import `@prisma/client`
- `schema.prisma` 之外并行维护手写 SQL schema 或 Kysely table mirror
- token 定义在 domain/core
- adapter 没有实现 port
- 空 adapter/presenter 增加层数
- use case 注入过多 repository 或 manager
- trace/log/transaction/idempotency 混入主 Service
- CLI/worker 拉起完整 Nest app context

### 重构策略

- 先补 characterization test，再动边界。
- 先抽 port，再移动 adapter。
- 先让 core service 可手写 `new`，再调整 Nest provider。
- 先做一个 use case 的完整链路，再复制到同类 use case。
- 不在一次变更里同时重命名领域概念和移动架构层。

### 文档同步

这些变化需要同步更新本地架构文档或 AGENTS guidance：

- Controller / UseCase / Port / Adapter 链路变化
- DI token 归属变化
- runtime config 解析方式变化
- Prisma schema、generated client 或数据库同步方式变化
- queue / async task 语义变化
- CLI、worker、HTTP 多入口复用方式变化
- boundary tests 的规则变化

### 交付表述

最终说明应包括：

- 改了哪些边界
- 数据流现在是什么
- 哪些文件承担入口、use case、port、adapter、composition root
- 跑了哪些验证命令
- 没跑的测试及原因
