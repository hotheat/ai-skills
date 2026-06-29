# Language

Shared vocabulary for every suggestion this skill makes. Use these terms exactly. Consistent language is the point.

## Terms

**Module**
Anything with an interface and an implementation. Applies to a function, class, package, or tier-spanning slice.
_Avoid_: unit, component, service.

**Interface**
Everything a caller must know to use the module correctly: type signature, invariants, ordering constraints, error modes, required configuration, and performance characteristics.
_Avoid_: API, signature.

**Implementation**
What is inside a module. Distinct from **adapter**: a thing can be a small adapter with a large implementation, or a large adapter with a small implementation.

**Depth**
Leverage at the interface. A module is **deep** when a large amount of behaviour sits behind a small interface. A module is **shallow** when the interface is nearly as complex as the implementation.

**Seam**
A place where behaviour can be altered without editing in that place. The location at which a module's interface lives.
_Avoid_: boundary.

**Adapter**
A concrete thing that satisfies an interface at a seam. Describes role, not substance.

**Leverage**
What callers get from depth: more capability per unit of interface they have to learn.

**Locality**
What maintainers get from depth: change, bugs, knowledge, and verification concentrated in one place.

## Principles

- **Depth is a property of the interface, not the implementation.** A deep module can be internally composed of small, swappable parts that are not part of the interface.
- **The deletion test.** Imagine deleting the module. If complexity vanishes, the module was pass-through. If complexity reappears across callers, the module was earning its keep.
- **The interface is the test surface.** Callers and tests cross the same seam.
- **One adapter means a hypothetical seam. Two adapters means a real seam.** Do not introduce a seam unless something actually varies across it.

## Relationships

- A **module** has one **interface** and one **implementation**.
- **Depth** is a property of a **module**, measured against its **interface**.
- A **seam** is where a **module**'s **interface** lives.
- An **adapter** sits at a **seam** and satisfies the **interface**.
- **Depth** produces **leverage** for callers and **locality** for maintainers.

## Rejected framings

- **Depth as implementation-lines divided by interface-lines**: rewards padding the implementation. Use depth-as-leverage instead.
- **Interface as only the TypeScript `interface` keyword or public methods**: too narrow.
- **Boundary**: overloaded with DDD's bounded context. Say **seam** or **interface**.
