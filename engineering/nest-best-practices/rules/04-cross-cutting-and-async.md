## Cross-Cutting、Async 与 Runtime State

### UseCase Wrapper

trace、log、transaction、idempotency、cancellation 不应污染主业务 Service。

推荐围绕 UseCase 包装：

- `LoggedUseCaseWrapper`
- `TracedUseCaseWrapper`
- `TransactionalUseCaseWrapper`
- `IdempotentUseCaseWrapper`
- `CancellableUseCaseWrapper`

默认链路：

```text
Controller
-> WrappedUseCase
-> Service
-> Ports
```

Wrapper 适合处理：

- trace span
- structured log
- transaction boundary
- idempotency key
- cancellation token
- retry policy
- metrics

### Transaction

transaction 是 use case 边界，不是 repository 私有细节。

推荐：

```text
TransactionalUseCaseWrapper
-> UnitOfWorkPort / TransactionManagerPort
-> Service
```

不要在多个 repository adapter 里各自决定事务边界。

### Trace 与 Log

trace/log 推荐通过 port 或 wrapper 注入。

规则：

- Service 可以记录业务阶段，但不应依赖具体 logger SDK。
- Adapter 可以记录外部调用细节。
- trace context 用 value object 或 plain context 传递，不要依赖全局 singleton。

### Async Queue

加入异步队列时，先决定 use case 的语义：

- 同步 use case：立即完成并返回结果。
- submit use case：创建任务，返回 task id。
- resume/worker use case：消费任务 payload，推进状态。
- cancel use case：请求取消并更新状态。

推荐链路：

```text
HTTP / CLI
-> SubmitTaskUseCase
-> AsyncTaskManagerPort
-> Queue Adapter
-> Worker
-> ExecuteTaskUseCase
-> Domain Ports
```

任务状态不要散落在 queue adapter 里。用 port 表达：

- `AsyncTaskManagerPort`
- `TaskStorePort`
- `RunStorePort`
- `TraceSinkPort`
- `ClockPort`

### Runtime State 建模

对 agent harness、queue、long-running job 这类系统，优先建模 value object：

- `RunId`
- `SessionId`
- `TaskId`
- `TaskCursor`
- `RunStatus`
- `TraceContext`
- `ModelRef`
- `ToolRef`
- `ContextWindow`

不要让 string 和 loose object 贯穿 controller、service、adapter。

### Idempotency

幂等不应靠 controller 临时判断。

推荐：

```text
IdempotentUseCaseWrapper
-> IdempotencyStorePort
-> Service
```

幂等 key 来源可以是 HTTP header、CLI flag、task payload，但进入 use case 后应变成明确 value object。

### Cancellation

取消能力需要独立语义。

推荐：

- `CancelRunUseCase`
- `CancellationTokenPort`
- `RunStorePort`
- `CancellableUseCaseWrapper`

不要只靠进程信号或 queue 删除任务表达业务取消。
