---
name: naming-conventions
description: >
  Standardized naming conventions for types, files, and artifacts across
  Clean Architecture layers. Language-specific conventions for Python,
  C#, TypeScript, Java, and Go.
  Use when naming new code artifacts or reviewing naming consistency.
  Trigger phrases: "naming convention", "how to name", "file naming",
  "class naming", "padrão de nomes", "convenção de nomenclatura".
  DO NOT trigger for: layer structure, code quality, or test organization.
allowed-tools: Read, Grep, Glob
---

# Naming Conventions

Standardized naming for all code artifacts across languages.

---

## File Naming

| Language | Convention | Example |
|----------|-----------|---------|
| Python | `snake_case.py` | `user_repository.py` |
| C# | `PascalCase.cs` | `UserRepository.cs` |
| TypeScript | `kebab-case.ts` or `PascalCase.ts` | `user-repository.ts` or `UserRepository.ts` |
| Java | `PascalCase.java` | `UserRepository.java` |
| Go | `snake_case.go` | `user_repository.go` |

---

## Type Naming

### Classes, Interfaces, Structs

| Language | Convention | Example |
|----------|-----------|---------|
| Python | `PascalCase` | `class UserRepository` |
| C# | `PascalCase` (interface prefix `I`) | `class UserRepository`, `interface IUserRepository` |
| TypeScript | `PascalCase` | `class UserRepository`, `interface UserRepository` |
| Java | `PascalCase` | `class UserRepository`, `interface UserRepository` |
| Go | `PascalCase` (exported), `camelCase` (unexported) | `type UserRepository struct` |

### Functions and Methods

| Language | Convention | Example |
|----------|-----------|---------|
| Python | `snake_case` | `def create_user()` |
| C# | `PascalCase` | `public void CreateUser()` |
| TypeScript | `camelCase` | `function createUser()` |
| Java | `camelCase` | `public void createUser()` |
| Go | `PascalCase` (exported), `camelCase` (unexported) | `func CreateUser()` |

### Variables and Fields

| Language | Convention | Example |
|----------|-----------|---------|
| Python | `snake_case` | `user_name = "..."` |
| C# | `camelCase` (local), `PascalCase` (property) | `var userName`, `public string UserName { get; }` |
| TypeScript | `camelCase` | `const userName = "..."` |
| Java | `camelCase` | `String userName = "..."` |
| Go | `camelCase` (local), `PascalCase` (exported) | `userName := "..."`, `UserName string` |

### Constants

| Language | Convention | Example |
|----------|-----------|---------|
| Python | `SCREAMING_SNAKE_CASE` | `MAX_RETRY_COUNT = 3` |
| C# | `PascalCase` | `public const int MaxRetryCount = 3` |
| TypeScript | `SCREAMING_SNAKE_CASE` | `const MAX_RETRY_COUNT = 3` |
| Java | `SCREAMING_SNAKE_CASE` | `public static final int MAX_RETRY_COUNT = 3` |
| Go | `PascalCase` or `SCREAMING_SNAKE_CASE` | `MaxRetryCount = 3` or `MAX_RETRY_COUNT = 3` |

---

## Clean Architecture Artifact Naming

### Repository

| Artifact | Python | C# | TypeScript | Java | Go |
|----------|--------|-----|-----------|------|-----|
| Interface (domain) | `OrderRepository` | `IOrderRepository` | `OrderRepository` | `OrderRepository` | `OrderRepository` |
| Implementation (infra) | `OrderDynamoRepository` | `OrderDynamoRepository` | `OrderDynamoRepository` | `OrderDynamoRepository` | `OrderDynamoRepository` |
| File | `order_repository.py` | `IOrderRepository.cs` | `order-repository.ts` | `OrderRepository.java` | `order_repository.go` |

### Use Case

| Artifact | Python | C# | TypeScript | Java | Go |
|----------|--------|-----|-----------|------|-----|
| Class | `CreateOrderUseCase` | `CreateOrderUseCase` | `CreateOrderUseCase` | `CreateOrderUseCase` | `CreateOrderUseCase` |
| File | `create_order_use_case.py` | `CreateOrderUseCase.cs` | `create-order-use-case.ts` | `CreateOrderUseCase.java` | `create_order_use_case.go` |
| Method | `execute()` | `Execute()` | `execute()` | `execute()` | `Execute()` |

### DTO (Data Transfer Object)

| Artifact | Python | C# | TypeScript | Java | Go |
|----------|--------|-----|-----------|------|-----|
| Input | `CreateOrderInput` | `CreateOrderInput` | `CreateOrderInput` | `CreateOrderInput` | `CreateOrderInput` |
| Output | `CreateOrderOutput` | `CreateOrderOutput` | `CreateOrderOutput` | `CreateOrderOutput` | `CreateOrderOutput` |
| Request | `CreateOrderRequest` | `CreateOrderRequest` | `CreateOrderRequest` | `CreateOrderRequest` | `CreateOrderRequest` |
| Response | `CreateOrderResponse` | `CreateOrderResponse` | `CreateOrderResponse` | `CreateOrderResponse` | `CreateOrderResponse` |

### Domain Service

| Artifact | Python | C# | TypeScript | Java | Go |
|----------|--------|-----|-----------|------|-----|
| Service | `PricingService` | `PricingService` | `PricingService` | `PricingService` | `PricingService` |
| File | `pricing_service.py` | `PricingService.cs` | `pricing-service.ts` | `PricingService.java` | `pricing_service.go` |

### Entity

| Artifact | Python | C# | TypeScript | Java | Go |
|----------|--------|-----|-----------|------|-----|
| Entity | `Order` | `Order` | `Order` | `Order` | `Order` |
| File | `order.py` | `Order.cs` | `order.ts` | `Order.java` | `order.go` |

### Value Object

| Artifact | Python | C# | TypeScript | Java | Go |
|----------|--------|-----|-----------|------|-----|
| Type | `Money` | `Money` | `Money` | `Money` | `Money` |
| File | `money.py` | `Money.cs` | `money.ts` | `Money.java` | `money.go` |

### Enum

| Artifact | Python | C# | TypeScript | Java | Go |
|----------|--------|-----|-----------|------|-----|
| Type | `OrderStatus` | `OrderStatus` | `OrderStatus` | `OrderStatus` | `OrderStatus` |
| File | `order_status.py` | `OrderStatus.cs` | `order-status.ts` | `OrderStatus.java` | `order_status.go` |
| Values | `PENDING`, `CONFIRMED` | `Pending`, `Confirmed` | `PENDING`, `CONFIRMED` | `PENDING`, `CONFIRMED` | `Pending`, `Confirmed` |

---

## Test Naming

| Artifact | Python | C# | TypeScript | Java | Go |
|----------|--------|-----|-----------|------|-----|
| Test class | `TestOrderRepository` | `OrderRepositoryTests` | `OrderRepository.test.ts` | `OrderRepositoryTest` | `TestOrderRepository` |
| Test file | `test_order_repository.py` | `OrderRepositoryTests.cs` | `order-repository.test.ts` | `OrderRepositoryTest.java` | `order_repository_test.go` |
| Test method | `test_save_order` | `SaveOrder_ValidOrder_SavesSuccessfully` | `it('saves order')` | `saveOrder_ValidOrder_SavesSuccessfully` | `TestSaveOrder` |

---

## Quick Reference Card

```
# Repository Interface
Python:     class OrderRepository(ABC)
C#:         public interface IOrderRepository
TypeScript: interface OrderRepository
Java:       public interface OrderRepository
Go:         type OrderRepository interface

# Use Case
Python:     class CreateOrderUseCase: def execute(self, input: CreateOrderInput)
C#:         public class CreateOrderUseCase: public CreateOrderOutput Execute(CreateOrderInput input)
TypeScript: class CreateOrderUseCase: execute(input: CreateOrderInput): CreateOrderOutput
Java:       public class CreateOrderUseCase: public CreateOrderOutput execute(CreateOrderInput input)
Go:         type CreateOrderUseCase struct: func (uc *CreateOrderUseCase) Execute(input CreateOrderInput) CreateOrderOutput
```
