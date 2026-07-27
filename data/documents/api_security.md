# API Security & OWASP API Top 10

## 1. Introduction

Application Programming Interfaces (APIs) form the backbone of modern web, mobile, and microservice architectures. Insecure APIs expose sensitive data stores and enterprise logic to automated attacks.

---

## 2. OWASP API Security Top 10

1. **API1: Broken Object Level Authorization (BOLA)**: Manipulating object IDs in endpoint requests (e.g., `/api/v1/users/1002` to `/api/v1/users/1003`) to access unauthorized user data.
2. **API2: Broken Authentication**: Flaws in token validation, credential handling, or session expiration allowing attackers to compromise user identities.
3. **API3: Broken Object Property Level Authorization**: Exposing or mutating unauthorized properties via payload manipulation (Mass Assignment).
4. **API4: Unrestricted Resource Consumption**: Lack of rate limiting or payload constraints, leading to DoS or high API bills.
5. **API5: Broken Function Level Authorization (BFLA)**: Accessing administrative API endpoints due to missing access control checks.
6. **API6: Unrestricted Access to Sensitive Business Flows**: Exploiting business logic (e.g., ticket purchasing or coupon redemption) via automation.
7. **API7: Server-Side Request Forgery (SSRF)**: API fetching remote resources specified by user input without validation.
8. **API8: Security Misconfiguration**: Unsecured CORS policies, verbose error tracebacks, or unencrypted HTTP transport.
9. **API9: Improper Inventory Management**: Exposing unpatched shadow APIs, deprecated endpoints, or staging environments.
10. **API10: Unsafe Consumption of APIs**: Insecurely processing data retrieved from third-party APIs without validation.

---

## 3. Recommended Remediation & Best Practices

- **Object-Level Access Control**: Enforce explicit authorization checks (`user_id == current_user.id`) for every object request at the controller layer.
- **API Gateway Enforcement**: Centralize rate limiting, TLS termination, WAF filtering, and OAuth2/JWT token validation.
- **Strict OpenAPI / Swagger Validation**: Validate incoming request bodies against strict JSON schemas to drop unexpected properties.
