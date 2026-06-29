# Deepening

How to deepen a cluster of shallow modules safely, given its dependencies. Assumes the vocabulary in [LANGUAGE.md](LANGUAGE.md).

## Dependency categories

Classify each candidate's dependencies. The category determines how the deepened module is tested across its seam.

### 1. In-process

Pure computation, in-memory state, no I/O. Always deepenable. Merge the modules and test through the new interface directly. No adapter needed.

### 2. Local-substitutable

Dependencies that have local test stand-ins, such as PGLite for Postgres or an in-memory filesystem. Deepenable when the stand-in exists. The deepened module is tested with the stand-in running in the test suite. The seam is internal; no port belongs at the module's external interface.

### 3. Remote but owned

Owned services across a network seam, such as internal APIs, queues, or microservices. Define a port at the seam. The deep module owns the logic; transport is injected as an adapter. Tests use an in-memory adapter. Production uses an HTTP, gRPC, or queue adapter.

Recommendation shape: "Define a port at the seam, implement an HTTP adapter for production and an in-memory adapter for testing, so the logic sits in one deep module even though it is deployed across a network."

### 4. True external

Third-party services you do not control, such as Stripe or Twilio. The deepened module takes the external dependency as an injected port. Tests provide a mock adapter.

## Seam discipline

- **One adapter means a hypothetical seam. Two adapters means a real seam.** Do not introduce a port unless at least two adapters are justified, typically production plus test.
- **Internal seams vs external seams.** A deep module can have internal seams private to its implementation and tests. Do not expose internal seams through the external interface just because tests use them.

## Testing strategy

- Old unit tests on shallow modules become waste once tests at the deepened module's interface exist. Delete or migrate them.
- Write new tests at the deepened module's interface.
- Tests assert observable outcomes through the interface, not internal state.
- Tests should survive internal refactors. They describe behaviour, not implementation.
