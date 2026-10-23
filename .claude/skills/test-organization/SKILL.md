---
name: test-organization
description: >
  Test structure, organization, and quality standards for Clean Architecture
  projects. Covers test file layout, test doubles, unit vs integration tests,
  and coverage exclusions. Examples in Python, C#, TypeScript, Java, and Go.
  Use when writing tests, reviewing test structure, or setting up test projects.
  Trigger phrases: "test structure", "test organization", "unit tests",
  "test coverage", "test doubles", "estrutura de testes", "testes unitários".
  DO NOT trigger for: layer structure, naming, or general code quality.
allowed-tools: Read, Grep, Glob
---

# Test Organization

Structure and standards for maintainable, reliable tests.

---

## Test File Structure

One test file per production file, mirroring the same folder hierarchy.

### Python

```
src/
└── domain/
    └── repositories/
        └── order_repository.py
tests/
└── domain/
    └── repositories/
        └── test_order_repository.py
```

### C#

```
src/
└── Domain/
    └── Repositories/
        └── IOrderRepository.cs
tests/
└── Domain/
    └── Repositories/
        └── OrderRepositoryTests.cs
```

### TypeScript

```
src/
└── domain/
    └── repositories/
        └── order-repository.ts
tests/
└── domain/
    └── repositories/
        └── order-repository.test.ts
```

### Java

```
src/main/java/com/example/
└── domain/
    └── repositories/
        └── OrderRepository.java
src/test/java/com/example/
└── domain/
    └── repositories/
        └── OrderRepositoryTest.java
```

### Go

```
src/
└── domain/
    └── repositories/
        └── order_repository.go
src/
└── domain/
    └── repositories/
        └── order_repository_test.go    # Same package
```

---

## Test Class Structure

One test class per production class. All test methods in that single class.

**Python**
```python
class TestOrderRepository:
    def test_save_order(self): ...
    def test_find_by_id(self): ...
    def test_find_all(self): ...
```

**C#**
```csharp
public class OrderRepositoryTests
{
    [Fact]
    public void SaveOrder_ValidOrder_SavesSuccessfully() { ... }

    [Fact]
    public void FindById_ExistingId_ReturnsOrder() { ... }
}
```

**TypeScript**
```typescript
describe('OrderRepository', () => {
    it('saves order', () => { ... });
    it('finds by id', () => { ... });
});
```

**Java**
```java
class OrderRepositoryTest {
    @Test
    void saveOrder_ValidOrder_SavesSuccessfully() { ... }

    @Test
    void findById_ExistingId_ReturnsOrder() { ... }
}
```

**Go**
```go
func TestOrderRepository_SaveOrder(t *testing.T) { ... }
func TestOrderRepository_FindById(t *testing.T) { ... }
```

---

## Test Doubles

Fakes, stubs, and spies each get their own file. Never inline in test classes.

### Python

```
tests/
├── doubles/
│   ├── __init__.py
│   ├── fake_order_repository.py
│   ├── stub_payment_client.py
│   └── spy_event_bus.py
└── domain/
    └── repositories/
        └── test_order_repository.py
```

**Fake** (working implementation, simplified):
```python
class FakeOrderRepository(OrderRepository):
    def __init__(self):
        self._orders: dict[str, Order] = {}

    def save(self, order: Order) -> None:
        self._orders[order.id] = order

    def find_by_id(self, id: str) -> Order | None:
        return self._orders.get(id)
```

**Stub** (returns fixed values):
```python
class StubPaymentClient(PaymentClient):
    def __init__(self, should_succeed: bool = True):
        self._should_succeed = should_succeed

    def charge(self, amount: Money) -> PaymentResult:
        return PaymentResult(success=self._should_succeed)
```

**Spy** (records calls):
```python
class SpyEventBus(EventBus):
    def __init__(self):
        self.published_events: list[DomainEvent] = []

    def publish(self, event: DomainEvent) -> None:
        self.published_events.append(event)
```

### C#

```
tests/
├── Doubles/
│   ├── FakeOrderRepository.cs
│   ├── StubPaymentClient.cs
│   └── SpyEventBus.cs
└── Domain/
    └── Repositories/
        └── OrderRepositoryTests.cs
```

---

## Unit vs Integration Tests

| Type | Scope | Dependencies | Speed | Location |
|------|-------|--------------|-------|----------|
| Unit | Single class | Fakes/stubs only | Fast | `tests/unit/` or same folder |
| Integration | Multiple classes | Real DB, HTTP | Slow | `tests/integration/` |

### Python

```
tests/
├── unit/
│   └── domain/
│       └── test_order.py
├── integration/
│   └── infrastructure/
│       └── test_order_dynamo_repository.py
└── conftest.py
```

### C#

```
tests/
├── Unit/
│   └── Domain/
│       └── OrderTests.cs
└── Integration/
    └── Infrastructure/
        └── OrderDynamoRepositoryTests.cs
```

---

## Coverage Exclusions

Files without testable logic must be explicitly excluded.

| Category | Python | C# | TypeScript | Java | Go |
|----------|--------|-----|-----------|------|-----|
| Pure data models | `# pragma: no cover` | `[ExcludeFromCodeCoverage]` | `/* istanbul ignore */` | `@ExcludeFromCodeCoverage` | `//go:build ignore` |
| Enums/constants | Class-level | Assembly-level | File-level | Class-level | File-level |
| Entry points | `if __name__ == "__main__"` | `Main` method | `index.ts` | `main` method | `main` function |

### Python

```python
# order.py
from dataclasses import dataclass

@dataclass
class Order:  # pragma: no cover
    id: str
    items: list[OrderItem]
    status: OrderStatus
```

### C#

```csharp
// Order.cs
[ExcludeFromCodeCoverage]
public record Order(string Id, List<OrderItem> Items, OrderStatus Status);
```

---

## Test Quality Checklist

- [ ] One test file per production file
- [ ] One test class per production class
- [ ] Test doubles in separate files, not inline
- [ ] Unit tests use fakes/stubs, not real infrastructure
- [ ] Integration tests are separated and marked
- [ ] Coverage exclusions applied to logic-free files
- [ ] Test names describe scenario and expected outcome
- [ ] No test depends on another test's execution order

---

## Naming Test Methods

| Pattern | Example |
|---------|---------|
| `MethodName_StateUnderTest_ExpectedBehavior` | `SaveOrder_ValidOrder_SavesSuccessfully` |
| `Should_ExpectedBehavior_When_StateUnderTest` | `Should_ThrowException_When_OrderIsInvalid` |
| `Given_Precondition_When_Action_Then_Result` | `Given_OrderExists_When_Deleting_Then_RemovesFromDb` |

| Language | Convention |
|----------|-----------|
| Python | `test_method_scenario_result` |
| C# | `Method_Scenario_Result` |
| TypeScript | `it('scenario result')` |
| Java | `method_scenario_result` |
| Go | `TestMethod_Scenario_Result` |
