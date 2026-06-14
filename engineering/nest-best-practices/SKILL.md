---
name: nest-best-practices
description: "NestJS 后端与 TypeScript clean architecture 规范。用于创建、重构、扩展或审查基于 NestJS 的 API、worker、CLI bridge、agent harness、异步任务系统，尤其适合建立 Controller 到 UseCase 到 Port 到 Adapter 链路、保持 core 框架无关、规划 DI token、composition root、runtime config、trace/log/transaction wrapper、entity/value object 和测试边界。"
---

# Nest Best Practices

默认把这类项目视为“NestJS runtime + framework-free core”的后端，而不是把所有业务代码写进 Nest provider graph。

## 默认立场

- 先检查仓库现状，再给结构建议；不要直接套模板。
- 保留仓库已有包管理器、lint、test、build、module layout 和命名约定。
- 默认把 NestJS 限制在 HTTP/runtime/composition root 层。
- 默认核心链路为 `Controller -> UseCase -> Port -> Adapter`。
- 默认数据库方案为 Prisma ORM + `schema.prisma` 驱动 schema 同步；不要把手写 SQL migration、Kysely table mirror 或裸 DB client query 作为默认方案。
- `UseCase` 是业务动作契约；`Service` 是 use case 契约实现。
- `Port` 是 core 需要的外部能力接口；`Adapter` 是 port 的具体实现。
- Controller 依赖 `UseCase`，不依赖具体 `Service`。
- Service 依赖 `Port` 和 core 内部对象，不直接依赖 infra adapter。
- 被 core use case 使用的 adapter 必须实现 port。
- 不添加空 request adapter、presenter、repository、factory。只有真实映射、编排或边界需求出现时再加。
- CLI、worker、test harness 若要复用业务能力，优先复用 framework-free core，而不是启动 Nest application context。

## 使用流程

1. 先检查项目的真实约束：
   - Nest 入口、module、controller、provider、config、test 命令
   - Prisma schema 位置、generate/push 命令、数据库连接配置和 client 注入方式
   - 业务代码是否已经混入 `@Injectable`、`@Inject`、HTTP exception、env 读取
   - use case、port、adapter、DI token 是否已经有命名体系
   - 是否同时存在 HTTP、CLI、worker、webhook、queue 等入口
2. 根据任务读取规则：
   - 目录和分层：读 `rules/01-project-shape.md`
   - UseCase / Port / Adapter：读 `rules/02-usecase-port-adapter.md`
   - DI、composition root、config：读 `rules/03-di-config-runtime.md`
   - async、trace、transaction、idempotency：读 `rules/04-cross-cutting-and-async.md`
   - 测试、review、交付：读 `rules/05-testing-review-and-delivery.md`
3. 设计或实现时坚持这些默认规则：
   - Controller 只做协议输入、鉴权上下文读取、payload 构造、异常映射
   - UseCase contract 定义输入输出；Service 实现业务编排
   - Service 使用 value object、entity、factory、port；不 import Nest 或 infra
   - Module 是 composition root，负责绑定 token、adapter、service、wrapper
   - Config 在 runtime 边界解析，再以 plain values 注入 core 或 adapter
   - PrismaClient 只在 infrastructure adapter、CLI/worker runtime 或 composition root 创建；core 不 import `@prisma/client`
4. 遇到这些情况时主动调整抽象层次：
   - Controller 开始解析复杂 body/query：先抽 validation payload 或 value object
   - Service 注入过多 port：抽 ContextFactory 或 RuntimeDependencyResolver
   - 多个 use case 重复 trace/log/transaction：抽 use case wrapper
   - 外部系统调用进入 core：先定义 port，再写 adapter
   - CLI/worker 想复用 API 服务：抽 framework-free service，不启动完整 Nest graph
   - 数据库 schema 变化：先更新 `schema.prisma` 和 Prisma contract tests，再运行 generate/push 命令
5. 做代码审查或重构时，优先找：
   - core 里出现 `@nestjs/*`、`@Injectable`、`@Inject`
   - Controller 直接依赖 concrete service
   - Service 直接 new 或 import infra adapter
   - DI token 分散在 core/domain 目录
   - config 在 import 时读取 `process.env` 或 `process.cwd()`
   - core 或 shared 直接 import `@prisma/client`
   - Prisma schema 之外并行维护手写 SQL schema 或 Kysely table mirror
   - 空 adapter/presenter 只增加层数
   - async queue、trace、transaction 污染主 use case 逻辑

## 何时不要照搬默认规则

- 小型 CRUD 且没有多入口、异步、审计、trace、外部 adapter 时，可以保持较薄结构。
- 团队已有稳定 DDD/module 规范时，先遵守本地命名，再套用边界原则。
- 只有一个协议入口且无复杂字段版本映射时，不要强行加 request adapter。
- 只有直接返回 DTO 且无 view shaping 时，不要强行加 presenter。
- Nest provider graph 已经是团队刻意选择时，可以保留，但要显式标注 core 被框架绑定的代价。

## 参考文件

- `rules/01-project-shape.md`
  - Nest 后端目录、单向依赖、文件落位、跨入口复用规则
- `rules/02-usecase-port-adapter.md`
  - UseCase、Service、Port、Adapter、Controller 的职责和数据流
- `rules/03-di-config-runtime.md`
  - DI token、composition root、runtime config、Nest 污染边界
- `rules/04-cross-cutting-and-async.md`
  - wrapper、trace、log、transaction、idempotency、queue 和取消
- `rules/05-testing-review-and-delivery.md`
  - 边界测试、单元测试、集成测试、review checklist 和验证命令
