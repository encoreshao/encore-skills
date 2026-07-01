# Code Review Style Guide

## Purpose

This guide defines the code review approach for GitLab merge requests, focusing on comprehensive analysis across security, logic, performance, and code quality dimensions.

## Review Principles

1. **Comprehensive but Prioritized:** Cover all four dimensions (security, logic, performance, quality) but prioritize critical issues
2. **Actionable Feedback:** Every comment should include specific recommendations, not just problems
3. **Context-Aware:** Consider the scope and purpose of the MR - don't over-engineer small fixes
4. **Educational:** Explain the "why" behind recommendations to help developers learn
5. **Balanced:** Acknowledge good practices alongside areas for improvement

## Review Structure

### 1. Overview Section

Provide a brief summary of the MR:
```markdown
## Review Summary

**Purpose:** [1-sentence description of what this MR accomplishes]
**Scope:** [Files changed, lines added/removed]
**Risk Level:** [Low/Medium/High based on changes]
**Recommendation:** [Approve/Request Changes/Needs Discussion]
```

### 2. Critical Issues (Blockers)

Issues that **must** be addressed before merging:
- Security vulnerabilities
- Logic errors that cause incorrect behavior
- Breaking changes without migration path
- Data loss or corruption risks

**Format:**
```markdown
### 🚨 Critical Issues

#### 1. [Category] Issue Title
**Location:** `file.py:123`
**Problem:** [Clear description of the issue]
**Impact:** [What could go wrong]
**Recommendation:** [Specific fix with code example if helpful]
```

### 3. Significant Concerns (Should Address)

Issues that should be fixed but may not block merge:
- Performance problems in critical paths
- Maintainability issues
- Missing error handling
- Unclear code that needs refactoring

**Format:**
```markdown
### ⚠️ Significant Concerns

#### 1. [Category] Issue Title
**Location:** `file.py:456`
**Concern:** [Description of the issue]
**Suggestion:** [Recommended approach]
```

### 4. Minor Suggestions (Nice to Have)

Non-blocking improvements:
- Style consistency
- Documentation improvements
- Code organization
- Test coverage enhancements

**Format:**
```markdown
### 💡 Minor Suggestions

- **file.py:789** - [Brief suggestion]
- **test.py:101** - [Brief suggestion]
```

### 5. Positive Highlights (Optional)

Acknowledge good practices to encourage continued improvement:
```markdown
### ✅ Positive Highlights

- Excellent test coverage for edge cases
- Clear variable naming throughout
- Good use of type hints
```

## Review Categories

### Security Concerns

Focus on OWASP Top 10 and common vulnerabilities:

**Check for:**
- SQL injection, XSS, CSRF vulnerabilities
- Authentication and authorization flaws
- Sensitive data exposure (hardcoded secrets, logging PII)
- Insecure dependencies or configurations
- Insufficient input validation
- Insecure deserialization
- Weak cryptography or missing encryption

**Example Comment:**
```markdown
#### 🚨 SQL Injection Vulnerability
**Location:** `api/users.py:45`
**Problem:** User input is directly interpolated into SQL query without sanitization.
```python
# Current (vulnerable)
query = f"SELECT * FROM users WHERE email = '{email}'"
```
**Impact:** Attacker can execute arbitrary SQL commands, potentially dumping the entire database.
**Recommendation:** Use parameterized queries:
```python
# Fixed
query = "SELECT * FROM users WHERE email = %s"
cursor.execute(query, (email,))
```
```

### Logic and Correctness

Focus on bugs, edge cases, and incorrect behavior:

**Check for:**
- Off-by-one errors
- Race conditions and concurrency issues
- Incorrect null/undefined handling
- Unhandled exceptions
- Edge case handling (empty arrays, negative numbers, etc.)
- Incorrect algorithm implementation
- State management issues

**Example Comment:**
```markdown
#### ⚠️ Potential Race Condition
**Location:** `cache.py:78`
**Concern:** The check-then-set pattern is not atomic, which could lead to cache inconsistency under concurrent access.
```python
# Current
if key not in cache:
    cache[key] = expensive_computation()
```
**Suggestion:** Use atomic operations or locking:
```python
# Better
cache.setdefault(key, expensive_computation())
# or use threading.Lock() for complex cases
```
```

### Performance Issues

Focus on scalability and efficiency:

**Check for:**
- N+1 query problems
- Inefficient algorithms (O(n²) where O(n) possible)
- Unnecessary database queries or API calls
- Memory leaks or excessive memory usage
- Missing indexes on database queries
- Blocking operations in async code
- Large file processing without streaming

**Example Comment:**
```markdown
#### ⚠️ N+1 Query Problem
**Location:** `views/orders.py:123`
**Concern:** Loading related data in a loop causes N+1 database queries.
```python
# Current - O(N) queries
for order in orders:
    customer = Customer.get(order.customer_id)  # N queries
```
**Impact:** With 1000 orders, this makes 1001 database queries. Response time increases linearly with order count.
**Suggestion:** Use eager loading:
```python
# Better - O(1) queries
orders = Order.select_related('customer').all()
for order in orders:
    customer = order.customer  # No additional query
```
```

### Code Quality and Maintainability

Focus on readability, patterns, and best practices:

**Check for:**
- Code duplication
- Overly complex functions (high cyclomatic complexity)
- Inconsistent naming conventions
- Missing or poor documentation
- Lack of type hints (Python) or types (TypeScript)
- Hard-to-test code (tight coupling, no dependency injection)
- Magic numbers or strings
- Inconsistent error handling patterns

**Example Comment:**
```markdown
#### 💡 Reduce Code Duplication
**Location:** `utils/formatters.py:45-78`
**Suggestion:** The date formatting logic is duplicated across three functions. Consider extracting to a shared helper:
```python
def _format_date_base(date, format_type):
    """Shared date formatting logic."""
    # Common logic here
    pass

def format_date_short(date):
    return _format_date_base(date, 'short')

def format_date_long(date):
    return _format_date_base(date, 'long')
```
This improves maintainability and reduces the risk of inconsistent formatting.
```

## Review Tone Guidelines

### Do:
✅ Be respectful and constructive
✅ Assume positive intent
✅ Provide specific examples and code snippets
✅ Explain the reasoning behind suggestions
✅ Acknowledge complexity and trade-offs
✅ Ask questions when unclear

### Don't:
❌ Use judgmental language ("this is terrible")
❌ Make personal criticisms
❌ Be vague ("this could be better")
❌ Demand changes without explanation
❌ Focus only on negatives
❌ Over-engineer small fixes

### Example Comparisons

**Bad:**
> This code is a mess. Rewrite it properly.

**Good:**
> This function handles multiple responsibilities (validation, database access, formatting). Consider splitting it into smaller functions to improve testability and readability. For example: `validate_input()`, `save_to_db()`, and `format_response()`.

---

**Bad:**
> You forgot error handling.

**Good:**
> If the API call fails, this will raise an unhandled exception and crash the request handler. Consider wrapping in try/except and returning a user-friendly error:
```python
try:
    response = api.call()
except ApiError as e:
    logger.error(f"API call failed: {e}")
    return {"error": "Service temporarily unavailable"}, 503
```

## Posting Review Comments

### General Comment (Overall Review)
Post the structured review (Overview, Critical Issues, Concerns, Suggestions) as a single comment on the MR.

### Line-Specific Comments
For critical or significant issues, also post comments on the specific lines of code to make them easier to address.

### Review Status
- **Approve:** No critical issues, minor suggestions only
- **Request Changes:** Critical or significant issues that must be addressed
- **Comment:** Providing feedback but deferring decision to another reviewer

## Example Complete Review

```markdown
## Review Summary

**Purpose:** Implements user authentication with JWT tokens
**Scope:** 8 files changed, +347/-89 lines
**Risk Level:** High (security-critical functionality)
**Recommendation:** Request Changes (2 critical security issues)

---

### 🚨 Critical Issues

#### 1. [Security] JWT Secret Hardcoded
**Location:** `auth/jwt.py:12`
**Problem:** JWT secret is hardcoded in the source code.
```python
SECRET_KEY = "my-secret-key-12345"
```
**Impact:** Anyone with access to the repository can forge authentication tokens, compromising all user accounts.
**Recommendation:** Load from environment variable:
```python
import os
SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable must be set")
```

#### 2. [Security] Missing Token Expiration Validation
**Location:** `auth/middleware.py:34`
**Problem:** Token expiration (`exp` claim) is not validated.
**Impact:** Expired tokens will still be accepted, allowing access after logout or token revocation.
**Recommendation:** Add expiration check:
```python
try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    # Expiration is automatically validated by decode()
except jwt.ExpiredSignatureError:
    return {"error": "Token expired"}, 401
```

---

### ⚠️ Significant Concerns

#### 1. [Performance] Database Query in Authentication Middleware
**Location:** `auth/middleware.py:45`
**Concern:** Every request triggers a database query to fetch user details.
**Suggestion:** Include essential user data in JWT payload to avoid database lookup on every request. Only query database when detailed user info is needed.

#### 2. [Logic] Race Condition in Token Refresh
**Location:** `auth/refresh.py:67`
**Concern:** Old token is invalidated before new token is issued, creating a gap where user could be logged out.
**Suggestion:** Issue new token first, then invalidate old token.

---

### 💡 Minor Suggestions

- **auth/jwt.py:28** - Add type hints to improve IDE support and catch errors early
- **tests/test_auth.py:15** - Add test case for expired token scenario
- **auth/middleware.py:12** - Extract magic string 'Bearer ' to constant

---

### ✅ Positive Highlights

- Excellent test coverage (94%)
- Clear separation of concerns between JWT generation and validation
- Good use of custom exceptions for different auth failure scenarios
- Documentation is clear and thorough
```

## When in Doubt

- **Prioritize security:** Better to flag a false positive than miss a real vulnerability
- **Consider maintainability:** Code is read more often than written
- **Respect scope:** Don't demand unrelated improvements
- **Ask for clarification:** If the intent is unclear, ask before assuming
