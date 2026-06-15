## DI、Composition Root 与 Runtime Config

### DI Token

DI token 属于 runtime composition root，不属于 core。

推荐：

```text
application/di/InjectionTokens.ts
```

按能力命名：

- `HarnessDITokens.AgentRuntime`
- `SessionDITokens.SessionStore`
- `ModelDITokens.ModelResolver`
- `ToolDITokens.ToolRegistry`
- `TaskDITokens.AsyncTaskManager`
- `TraceDITokens.TraceSink`
- `LogDITokens.RunLogger`

小项目可用一个 `InjectionTokens.ts`，大项目可按 bounded context 拆 token 文件，但仍放在 application/di 边界。

### Composition Root

Nest module 是 composition root。

它负责：

- 绑定 port 到 adapter
- 构造 framework-free service
- 包装 use case wrapper
- 解析 runtime config
- 提供 controller 依赖

推荐用 `useFactory` 构造 core service：

```text
provider token
-> useFactory(port, factory, logger)
-> new CoreService(...)
```

`useClass` 更适合无 primitive constructor 参数、需要 Nest 管理生命周期的 infrastructure adapter。

### Core 禁止事项

core 中避免：

- `@nestjs/*`
- `@Injectable`
- `@Inject`
- DI token
- `process.env`
- `process.cwd()`
- HTTP exception
- DB client / SDK concrete class
  - `@prisma/client` generated types or PrismaClient

core class 应该可以在单元测试里直接 `new`。

### Runtime Config

配置解析放在 runtime 边界。

推荐：

- API config：`infrastructure/config/*`
- CLI config：`cli/src/*`
- Worker config：worker entry 或 worker runtime module

规则：

- 不要在 import 时解析 static config。
- 不要在 core 读取 env。
- 解析函数接受 override，方便测试。
- module provider factory 中调用 config resolver，然后把 plain value 传给 adapter 或 service。
- Prisma `DATABASE_URL` 解析属于 runtime 边界；PrismaClient 在 infrastructure adapter、Prisma service/factory、CLI/worker composition root 创建。
- `schema.prisma` 是数据库 schema 的默认来源；用项目命令运行 Prisma format/generate/push，不新增并行手写 SQL migration 流程。

反模式：

```text
static readonly DATA_ROOT = process.cwd()
```

推荐：

```text
resolveDataRoot({ envRoot, cwd, moduleUrl })
```

### 多入口复用

HTTP、CLI、worker、webhook、queue 可以共享 use case contract 和 framework-free service。

不推荐：

```text
CLI -> NestFactory.createApplicationContext(RootModule)
```

推荐：

```text
CLI runtime
-> construct core service with plain adapters
-> create Prisma adapter/client in CLI composition root when database access is needed
-> execute use case
```

如果依赖很多，用 `RuntimeDependencyResolver` 或 `UseCaseContextFactory` 聚合，不让 use case 变成上帝对象。

### Module 边界

- `RootModule` 只组装顶层模块。
- feature module 绑定本 feature 的 controller、use case、port、adapter。
- 不要让 controller 自己 import adapter。
- 不要在 module 外到处 `new` infrastructure adapter，除非这是 CLI/worker 的独立 composition root。
