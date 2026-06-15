## Nest 项目形态与目录分层

默认目标是让 Nest 成为 runtime 和 composition root，让业务 core 保持普通 TypeScript。

### 推荐目录结构

```text
src/
  application/
    api/
      http-rest/
        controller/
    di/
      RootModule.ts
      FeatureModule.ts
      InjectionTokens.ts
    ServerApplication.ts
  core/
    common/
      usecase/
      value-object/
      observability/
    domain/
      <domain>/
        usecase/
        port/
        entity/
        value-object/
        factory/
    service/
      <domain>/
  infrastructure/
    adapter/
      persistence/
      prisma/
      model/
      queue/
      observability/
    config/
```

若仓库已经是 monorepo，可把 Nest app 放在 `apps/api/`，共享 contract 放在 `packages/shared/`，纯业务或数据规则放在 `packages/*`。

### 边界规则

- `application/`
  - Nest module、controller、guard、interceptor、pipe、HTTP exception mapping、composition root
  - 可以 import core 和 infrastructure，用于绑定依赖
- `core/`
  - UseCase contract、Service implementation、Port、Entity、Value Object、Factory
  - 不 import `@nestjs/*`
  - 不使用 `@Injectable`、`@Inject`
  - 不读取 runtime env
  - 不 import infrastructure adapter
- `infrastructure/`
  - 文件系统、数据库、HTTP client、model provider、queue、logger、trace sink 等 adapter
  - adapter 必须实现 core port，除非它只服务 Nest runtime 本身
- `packages/shared/`
  - 跨 app contract、DTO schema、轻量 helper
  - 不 import Nest、Node adapter、React、CLI、runtime config

### 单向依赖

```text
shared contracts
-> core
-> application composition root
-> infrastructure adapters
```

运行时绑定方向由 composition root 完成：

```text
Controller
-> UseCase token
-> Service
-> Port token
-> Adapter
```

### 文件落位决策表

| 场景 | 推荐位置 |
|------|----------|
| HTTP route、body/query/param 读取 | `application/api/http-rest/controller/*` |
| 业务动作接口 | `core/**/usecase/*UseCase.ts` |
| 业务动作实现 | `core/service/**/**Service.ts` |
| 外部能力接口 | `core/**/port/*Port.ts` |
| 外部能力实现 | `infrastructure/adapter/**/**Adapter.ts` |
| Prisma schema | `prisma/schema.prisma` 或仓库既有 Prisma schema 位置 |
| Prisma client factory / service | `infrastructure/adapter/persistence/prisma/*` 或 runtime composition root |
| DI token | `application/di/InjectionTokens.ts` |
| Nest provider 绑定 | `application/di/*Module.ts` |
| runtime env/path/config | `infrastructure/config/*` 或 runtime entry |
| 共享 DTO/contract | `packages/shared` 或 `src/shared` |
| 领域状态约束 | `core/**/entity`、`core/**/value-object` |

### 演进策略

- 新业务默认先定义 use case contract 和输入输出。
- 需要外部系统时先定义 port，再实现 adapter。
- 需要跨入口复用时抽 framework-free service，不复用 Nest controller。
- 重复编排出现两次以上再抽 factory、resolver 或 wrapper。
- 数据库 schema 默认由 Prisma ORM + `schema.prisma` 管理；schema 修改后运行项目已有的 Prisma generate/sync 命令。

### 反模式

- 把业务逻辑塞进 controller。
- core service 使用 Nest decorator。
- core 或 shared 直接 import `@prisma/client`。
- 在 `schema.prisma` 之外并行维护手写 SQL schema 或 Kysely table mirror。
- CLI 或 worker 通过 `NestFactory.createApplicationContext()` 拉完整 HTTP app。
- DI token 放在 domain/core 目录。
- `src/lib` 成为无法归类的兜底目录。
- 为了“看起来干净”创建空 adapter、presenter、manager。
