---
name: code-quality-principles
description: >
  Universal code quality rules: SOLID principles, type safety, dead code
  elimination, defensive code boundaries, and comment guidelines.
  Language-agnostic with examples in Python, C#, TypeScript, Java, and Go.
  Use when reviewing code quality, refactoring, or establishing coding standards.
  Trigger phrases: "code quality", "solid principles", "type safety",
  "clean code", "dead code", "qualidade de código", "princípios solid".
  DO NOT trigger for: layer structure, naming, or test organization.
allowed-tools: Read, Grep, Glob
---

# Code Quality Principles

Universal rules for maintainable, readable, and robust code.

---

## 1. SOLID Principles

### Single Responsibility Principle (SRP)

One class does one thing. If describing a method requires "and", split it.

**Python**
```python
# Violation: does two things
class OrderService:
    def create_order_and_send_email(self, data): ...

# Correct: separate responsibilities
class CreateOrderUseCase:
    def execute(self, input: CreateOrderInput) -> CreateOrderOutput: ...

class SendOrderEmailUseCase:
    def execute(self, input: SendEmailInput) -> None: ...
```

**C#**
```csharp
// Violation
public class OrderService
{
    public void CreateOrderAndSendEmail(OrderData data) { ... }
}

// Correct
public class CreateOrderUseCase
{
    public CreateOrderOutput Execute(CreateOrderInput input) { ... }
}

public class SendOrderEmailUseCase
{
    public void Execute(SendEmailInput input) { ... }
}
```

**TypeScript**
```typescript
// Violation
class OrderService {
    createOrderAndSendEmail(data: OrderData): void { ... }
}

// Correct
class CreateOrderUseCase {
    execute(input: CreateOrderInput): CreateOrderOutput { ... }
}

class SendOrderEmailUseCase {
    execute(input: SendEmailInput): void { ... }
}
```

**Java**
```java
// Violation
public class OrderService {
    public void createOrderAndSendEmail(OrderData data) { ... }
}

// Correct
public class CreateOrderUseCase {
    public CreateOrderOutput execute(CreateOrderInput input) { ... }
}

public class SendOrderEmailUseCase {
    public void execute(SendEmailInput input) { ... }
}
```

**Go**
```go
// Violation
type OrderService struct{}
func (s *OrderService) CreateOrderAndSendEmail(data OrderData) { ... }

// Correct
type CreateOrderUseCase struct{}
func (uc *CreateOrderUseCase) Execute(input CreateOrderInput) CreateOrderOutput { ... }

type SendOrderEmailUseCase struct{}
func (uc *SendOrderEmailUseCase) Execute(input SendEmailInput) { ... }
```

---

### Open/Closed Principle (OCP)

Extend behavior via new classes or decorators, not by modifying stable code.

**Python**
```python
# Correct: new behavior via decorator
class LoggingOrderRepository:
    def __init__(self, decorated: OrderRepository):
        self._decorated = decorated

    def save(self, order: Order) -> None:
        logger.info(f"Saving order {order.id}")
        self._decorated.save(order)
```

**C#**
```csharp
// Correct: new behavior via decorator
public class LoggingOrderRepository : IOrderRepository
{
    private readonly IOrderRepository _decorated;

    public LoggingOrderRepository(IOrderRepository decorated)
    {
        _decorated = decorated;
    }

    public void Save(Order order)
    {
        _logger.LogInformation($"Saving order {order.Id}");
        _decorated.Save(order);
    }
}
```

---

### Liskov Substitution Principle (LSP)

Any implementation of an interface must be substitutable without changing caller behavior.

**Violation**: Throwing `NotImplementedException` in a subclass method.
**Violation**: Strengthening preconditions in a subclass.

---

### Interface Segregation Principle (ISP)

Define narrow, focused interfaces. No caller should be forced to depend on methods it does not use.

**Python**
```python
# Violation: fat interface
class OrderRepository(ABC):
    def save(self, order: Order) -> None: ...
    def find_by_id(self, id: str) -> Order: ...
    def find_all(self) -> list[Order]: ...
    def delete(self, id: str) -> None: ...
    def export_csv(self) -> str: ...        # Not all callers need this
    def send_webhook(self) -> None: ...     # Not all callers need this

# Correct: segregated interfaces
class OrderWriter(ABC):
    def save(self, order: Order) -> None: ...

class OrderReader(ABC):
    def find_by_id(self, id: str) -> Order: ...
    def find_all(self) -> list[Order]: ...
```

**C#**
```csharp
// Violation
public interface IOrderRepository
{
    void Save(Order order);
    Order FindById(string id);
    List<Order> FindAll();
    void Delete(string id);
    string ExportCsv();           // Not all callers need this
    void SendWebhook();           // Not all callers need this
}

// Correct
public interface IOrderWriter
{
    void Save(Order order);
}

public interface IOrderReader
{
    Order FindById(string id);
    List<Order> FindAll();
}
```

---

### Dependency Inversion Principle (DIP)

High-level modules depend on abstractions, never on concrete infrastructure.

**Python**
```python
# Correct: use case depends on abstraction
class CreateOrderUseCase:
    def __init__(self, order_repo: OrderRepository):  # Interface, not concrete
        self._order_repo = order_repo
```

**C#**
```csharp
// Correct
public class CreateOrderUseCase
{
    private readonly IOrderRepository _orderRepository;  // Interface

    public CreateOrderUseCase(IOrderRepository orderRepository)
    {
        _orderRepository = orderRepository;
    }
}
```

**Java**
```java
// Correct
public class CreateOrderUseCase {
    private final OrderRepository orderRepository;  // Interface

    public CreateOrderUseCase(OrderRepository orderRepository) {
        this.orderRepository = orderRepository;
    }
}
```

---

## 2. Type Safety

| Rule | Python | C# | TypeScript | Java | Go |
|------|--------|-----|-----------|------|-----|
| Public method signatures | Full type hints | Full types | Full types | Full types | Full types |
| Instance fields | Type hints | Auto-properties | Type annotations | Field types | Struct tags |
| Avoid | `Any` without comment | `object` without comment | `any` without comment | `Object` without comment | `interface{}` without comment |

**Python**
```python
# Correct
def calculate_total(items: list[OrderItem], tax_rate: Decimal) -> Money: ...

# Violation
def calculate_total(items, tax_rate): ...  # No types
```

**C#**
```csharp
// Correct
public Money CalculateTotal(List<OrderItem> items, decimal taxRate) { ... }

// Violation
public object CalculateTotal(object items, object taxRate) { ... }
```

---

## 3. Method-Level Single Responsibility

Each method does exactly one thing. Extract isolable logic into private methods.

**Python**
```python
# Correct
class OrderProcessor:
    def process(self, order: Order) -> None:
        self._validate(order)
        self._calculate_totals(order)
        self._persist(order)

    def _validate(self, order: Order) -> None: ...
    def _calculate_totals(self, order: Order) -> None: ...
    def _persist(self, order: Order) -> None: ...
```

---

## 4. No Dead Code

Remove after implementing or refactoring:
- Unused imports, variables, methods, classes, types, constants, files
- Commented-out code
- "Might be useful later" stubs
- Old implementations alongside new ones

---

## 5. No Defensive Code for Impossible Scenarios

**Do validate at boundaries:**
- User input (forms, CLI args)
- External API responses
- Message payloads

**Do not validate:**
- States the type system guarantees cannot occur
- Framework-guaranteed invariants
- Internal contract violations (fail fast instead)

**Python**
```python
# Correct: validate at boundary
def create_user(email: str, age: int) -> User:
    if not email or "@" not in email:
        raise ValueError("Invalid email")
    if age < 0 or age > 150:
        raise ValueError("Invalid age")
    return User(email=email, age=age)

# Violation: defensive internal check
def _calculate_discount(self, user: User) -> Decimal:
    if user is None:  # Impossible: typed as non-nullable
        return Decimal(0)
    ...
```

---

## 6. Comments: When and Only When

**Write when the why is non-obvious:**
- Hidden constraint or subtle invariant
- Workaround for a specific external bug
- Behavior that would surprise a competent reader

**Never write:**
- What the code does (well-named identifiers do that)
- References to current task, ticket, or PR
- Docstrings that restate the signature

**Python**
```python
# Correct
# AWS S3 has a 5TB limit per object; we chunk uploads above 4TB
CHUNK_SIZE = 4 * 1024 * 1024 * 1024  # 4GB

# Violation
# This function calculates the total
def calculate_total(self) -> Decimal: ...
```
