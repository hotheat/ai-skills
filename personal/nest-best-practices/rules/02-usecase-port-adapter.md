## UseCase、Port、Adapter 与数据流

### 角色定义

- `UseCase`
  - 业务动作契约。
  - 定义 payload、result 和 `execute(...)`。
  - Controller、CLI、worker 可以依赖它。
- `Service`
  - UseCase 契约实现。
  - 编排 value object、entity、factory、port。
  - 不直接依赖 Nest 或 infrastructure adapter。
- `Port`
  - core 所需外部能力接口。
  - 例如 repository、model client、queue、trace sink、logger、clock、asset storage。
- `Adapter`
  - Port 的具体实现。
  - 例如 file-system repository、Prisma repository、OpenAI adapter、S3 adapter、BullMQ adapter。
- `Controller`
  - 协议入口。
  - 读取 params/body/query/context，构造 use case payload，调用 use case，映射 HTTP response。

### 默认数据流

HTTP:

```text
HTTP request
-> Controller
-> value object / payload
-> UseCase
-> Service
-> Port
-> Infrastructure Adapter
-> external system
-> result DTO
```

CLI 或 worker:

```text
CLI / worker input
-> command payload / task payload
-> UseCase
-> Service
-> Port
-> Adapter
```

### Controller 规则

- Controller 可以做：
  - route param decode
  - body/query 读取
  - auth/session context 读取
  - value object 构造
  - use case 调用
  - HTTP exception 映射
- Controller 不应做：
  - 业务决策
  - repository 查询编排
  - 调用 concrete service
  - 调用 infra adapter
  - 复杂 response shaping

请求 adapter 只在这些场景出现：

- 多协议复用同一套输入映射
- body 字段版本多、兼容逻辑复杂
- 输入校验需要独立测试
- HTTP、CLI、webhook 共享相同 use case contract

没有这些场景时，Controller 直接 build payload 更清晰。

### Service 规则

- Service 构造函数只接收 port、factory、resolver、logger wrapper 等抽象依赖。
- Service 内使用 value object 表达约束，不让 string/plain object 到处漂。
- Service 返回 use case result 或 shared DTO，不返回 HTTP response。
- Service 变厚时优先拆：
  - domain factory
  - context factory
  - dependency resolver
  - use case wrapper

### Port 规则

- Port 名称表达能力，不表达实现。
- 示例：
  - `CharacterManifestRepositoryPort`
  - `AiExplanationPort`
  - `AsyncTaskManagerPort`
  - `TraceSinkPort`
  - `ClockPort`
- Port 放在 core 中靠近使用它的 domain。
- 若多个 domain 都要用，放在 `core/common`。

### Adapter 规则

- Adapter 名称表达实现。
- 示例：
  - `FileSystemCharacterManifestRepositoryAdapter`
  - `OpenAiExplanationAdapter`
  - `BullMqAsyncTaskManagerAdapter`
  - `ConsoleLoggerAdapter`
- 被 core use case 使用的 adapter 必须 `implements Port`。
- Adapter 可以使用 Nest、Node、SDK、DB client、HTTP client。
- Adapter 不应反向 import core service。

### Presenter 规则

Presenter 不是默认层。

只在这些场景出现：

- 多个 controller 共享复杂 response shaping
- HTTP response 与 use case result 差异很大
- 需要 API version、locale、view model、field masking
- 需要单测 response mapping

简单 DTO 直接由 controller 返回。
