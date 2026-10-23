---
name: clean-architecture-rules
description: >
  Quick reference index for Clean Architecture and DDD rules. Points to
  detailed skills for layer structure, code quality, naming conventions,
  and test organization.
  Use as a starting point when you need architectural guidance.
  Trigger phrases: "clean architecture", "ddd", "architecture overview",
  "code review checklist", "arquitetura limpa", "visão geral arquitetura".
  DO NOT auto-trigger for all code tasks; consult on demand only.
allowed-tools: Read, Grep, Glob
---

# Clean Architecture Rules — Quick Reference

Index of architectural skills. Consult the detailed skill for your specific need.

---

## Skills Overview

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| [`architecture-layer-structure`](../architecture-layer-structure/) | Folder structure, layer dependencies | Setting up projects, reviewing boundaries |
| [`code-quality-principles`](../code-quality-principles/) | SOLID, type safety, dead code | Code review, refactoring |
| [`naming-conventions`](../naming-conventions/) | Type, file, and artifact naming | Creating new code, reviewing consistency |
| [`test-organization`](../test-organization/) | Test structure, doubles, coverage | Writing tests, reviewing test code |

---

## Layer Structure (Summary)

```
presentation → application → domain
infrastructure → application → domain
```

**Forbidden**: `domain → application`, `domain → infrastructure`, `application → infrastructure`

See [`architecture-layer-structure`](../architecture-layer-structure/) for full details.

---

## Code Quality (Summary)

- **SRP**: One class, one responsibility
- **OCP**: Extend via new classes, not modification
- **LSP**: Subtypes must be substitutable
- **ISP**: Narrow interfaces, no forced dependencies
- **DIP**: Depend on abstractions, not concretions

See [`code-quality-principles`](../code-quality-principles/) for examples in your language.

---

## Naming (Summary)

| Artifact | Pattern |
|----------|---------|
| Repository interface | `IOrderRepository` / `OrderRepository` |
| Repository impl | `OrderDynamoRepository` |
| Use case | `CreateOrderUseCase` |
| DTO | `CreateOrderInput` / `CreateOrderOutput` |
| Domain service | `PricingService` |

See [`naming-conventions`](../naming-conventions/) for language-specific conventions.

---

## Tests (Summary)

- One test file per production file
- One test class per production class
- Test doubles in separate files
- Unit tests use fakes, not real infrastructure

See [`test-organization`](../test-organization/) for full structure.

---

## Language Support

All skills provide examples in:
- **Python**
- **C#**
- **TypeScript**
- **Java**
- **Go**

---

## Code Review Checklist

Quick checklist for reviews. Expand sections via the detailed skills.

### Architecture
- [ ] Layer import directions respected
- [ ] Domain has zero external dependencies
- [ ] Application imports only from domain

### Quality
- [ ] SOLID principles followed
- [ ] All signatures fully typed
- [ ] No dead code
- [ ] No defensive code for impossible scenarios

### Naming
- [ ] Conventions followed per language
- [ ] Artifacts named per Clean Architecture patterns

### Tests
- [ ] Structure mirrors production
- [ ] Test doubles in separate files
- [ ] Coverage exclusions applied
