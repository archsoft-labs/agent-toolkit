---
name: architecture-layer-structure
description: >
  Defines Clean Architecture layer structure, folder organization, and
  dependency rules between layers. Language-agnostic patterns with examples
  in Python, C#, TypeScript, Java, and Go.
  Use when setting up new projects, reviewing architecture, or refactoring
  layer boundaries.
  Trigger phrases: "layer structure", "folder structure", "clean architecture",
  "project structure", "dependency rules", "estrutura de camadas", "arquitetura".
  DO NOT trigger for: naming conventions, test structure, or code quality rules.
allowed-tools: Read, Grep, Glob
---

# Architecture Layer Structure

Clean Architecture layer organization and dependency rules.

---

## Layer Definitions

| Layer | Responsibility | Contains |
|-------|---------------|----------|
| `domain/` | Business logic, entities, rules | Entities, value objects, domain events, repository interfaces |
| `application/` | Use case orchestration | Use cases, application services, DTOs, ports |
| `infrastructure/` | External concerns | DB adapters, HTTP clients, message brokers, cloud SDKs |
| `presentation/` | Entry points, I/O translation | Controllers, CLI handlers, Lambda entry points |

---

## Folder Structure by Language

### Python

```
src/
├── domain/
│   ├── entities/
│   │   ├── __init__.py
│   │   └── order.py
│   ├── value_objects/
│   │   └── money.py
│   ├── events/
│   │   └── order_created.py
│   └── repositories/
│       └── order_repository.py      # Interface only
├── application/
│   ├── use_cases/
│   │   └── create_order_use_case.py
│   ├── dtos/
│   │   └── create_order_input.py
│   └── ports/
│       └── event_bus.py             # Interface only
├── infrastructure/
│   ├── database/
│   │   └── order_dynamo_repository.py
│   ├── messaging/
│   │   └── sns_event_bus.py
│   └── http/
│       └── payment_client.py
└── presentation/
    ├── api/
    │   └── order_controller.py
    └── cli/
        └── order_cli.py
```

### C#

```
src/
├── Domain/
│   ├── Entities/
│   │   └── Order.cs
│   ├── ValueObjects/
│   │   └── Money.cs
│   ├── Events/
│   │   └── OrderCreated.cs
│   └── Repositories/
│       └── IOrderRepository.cs      # Interface only
├── Application/
│   ├── UseCases/
│   │   └── CreateOrderUseCase.cs
│   ├── DTOs/
│   │   └── CreateOrderInput.cs
│   └── Ports/
│       └── IEventBus.cs             # Interface only
├── Infrastructure/
│   ├── Database/
│   │   └── OrderDynamoRepository.cs
│   ├── Messaging/
│   │   └── SnsEventBus.cs
│   └── Http/
│       └── PaymentClient.cs
└── Presentation/
    ├── Api/
    │   └── OrderController.cs
    └── Cli/
        └── OrderCli.cs
```

### TypeScript

```
src/
├── domain/
│   ├── entities/
│   │   └── Order.ts
│   ├── value-objects/
│   │   └── Money.ts
│   ├── events/
│   │   └── OrderCreated.ts
│   └── repositories/
│       └── OrderRepository.ts       # Interface only
├── application/
│   ├── use-cases/
│   │   └── CreateOrderUseCase.ts
│   ├── dtos/
│   │   └── CreateOrderInput.ts
│   └── ports/
│       └── EventBus.ts              # Interface only
├── infrastructure/
│   ├── database/
│   │   └── OrderDynamoRepository.ts
│   ├── messaging/
│   │   └── SnsEventBus.ts
│   └── http/
│       └── PaymentClient.ts
└── presentation/
    ├── api/
    │   └── OrderController.ts
    └── cli/
        └── OrderCli.ts
```

### Java

```
src/main/java/com/example/
├── domain/
│   ├── entities/
│   │   └── Order.java
│   ├── valueobjects/
│   │   └── Money.java
│   ├── events/
│   │   └── OrderCreated.java
│   └── repositories/
│       └── OrderRepository.java     // Interface only
├── application/
│   ├── usecases/
│   │   └── CreateOrderUseCase.java
│   ├── dtos/
│   │   └── CreateOrderInput.java
│   └── ports/
│       └── EventBus.java            // Interface only
├── infrastructure/
│   ├── database/
│   │   └── OrderDynamoRepository.java
│   ├── messaging/
│   │   └── SnsEventBus.java
│   └── http/
│       └── PaymentClient.java
└── presentation/
    ├── api/
    │   └── OrderController.java
    └── cli/
        └── OrderCli.java
```

### Go

```
src/
├── domain/
│   ├── entities/
│   │   └── order.go
│   ├── valueobjects/
│   │   └── money.go
│   ├── events/
│   │   └── order_created.go
│   └── repositories/
│       └── order_repository.go      // Interface only
├── application/
│   ├── usecases/
│   │   └── create_order_use_case.go
│   ├── dtos/
│   │   └── create_order_input.go
│   └── ports/
│       └── event_bus.go             // Interface only
├── infrastructure/
│   ├── database/
│   │   └── order_dynamo_repository.go
│   ├── messaging/
│   │   └── sns_event_bus.go
│   └── http/
│       └── payment_client.go
└── presentation/
    ├── api/
    │   └── order_controller.go
    └── cli/
        └── order_cli.go
```

---

## Dependency Rules

### Allowed Directions

```
presentation → application → domain
infrastructure → application → domain
infrastructure → domain
```

### Forbidden Directions

```
domain → application        # Domain must not know use cases
domain → infrastructure     # Domain must not know adapters
domain → presentation       # Domain must not know entry points
application → infrastructure # Application must not know concrete adapters
application → presentation   # Application must not know controllers
```

### Import Rules by Language

| Language | Allowed Import Pattern | Forbidden Pattern |
|----------|----------------------|-------------------|
| Python | `from domain.entities import Order` | `from application.use_cases import ...` in domain |
| C# | `using Domain.Entities;` | `using Application.UseCases;` in Domain |
| TypeScript | `import { Order } from '../domain/entities'` | `import { ... } from '../application'` in domain |
| Java | `import com.example.domain.entities.Order` | `import com.example.application...` in domain |
| Go | `import "myapp/domain/entities"` | `import "myapp/application"` in domain |

---

## Layer Isolation Checklist

- [ ] `domain/` has zero external framework imports
- [ ] `application/` imports only from `domain/`
- [ ] `infrastructure/` implements interfaces from `domain/` or `application/`
- [ ] `presentation/` calls use cases, never repositories directly
- [ ] No circular dependencies between layers
