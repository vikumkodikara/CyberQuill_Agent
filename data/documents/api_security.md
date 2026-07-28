---
title: API Security & OWASP API Top 10
categories: [Vulnerability Management, Cloud Security]
keywords: [API security, BOLA, BFLA, OAuth, JWT, rate limiting, SSRF, REST]
frameworks: [OWASP API Top 10, OAuth 2.0, OpenAPI 3.0]
---

# API Security & OWASP API Top 10

## Overview

Application Programming Interfaces (APIs) form the backbone of modern web, mobile, and microservice architectures. Insecure APIs expose sensitive data stores and enterprise logic to automated attacks. The OWASP API Security Top 10 identifies the most critical API-specific risks organizations must address.

## Key Concepts & Attack Vectors

1. **API1: Broken Object Level Authorization (BOLA)** — Manipulating object IDs in endpoint requests to access unauthorized user data.
2. **API2: Broken Authentication** — Flaws in token validation, credential handling, or session expiration.
3. **API4: Unrestricted Resource Consumption** — Lack of rate limiting leading to denial of service or excessive API costs.
4. **API5: Broken Function Level Authorization (BFLA)** — Accessing administrative endpoints due to missing access control checks.
5. **API7: Server-Side Request Forgery (SSRF)** — API fetching remote resources specified by user input without validation.
6. **API8: Security Misconfiguration** — Unsecured CORS policies, verbose error tracebacks, or unencrypted HTTP transport.

## Detection & Indicators

- Monitor for sequential object ID enumeration patterns in API access logs (BOLA indicator).
- Alert on authentication failures exceeding thresholds and token reuse anomalies.
- Track API rate limit violations and unusual request volume spikes per client.
- Detect SSRF attempts via outbound requests to internal IP ranges (169.254.x.x, 10.x.x.x).
- Scan API specifications for undocumented shadow endpoints and deprecated versions.

## Mitigation & Best Practices

- **Object-Level Access Control**: Enforce explicit authorization checks for every object request at the controller layer.
- **API Gateway Enforcement**: Centralize rate limiting, TLS termination, WAF filtering, and OAuth2/JWT validation.
- **Strict Schema Validation**: Validate incoming request bodies against OpenAPI/JSON schemas to reject unexpected properties.
- **API Inventory Management**: Maintain complete API inventory with versioning, deprecation, and security review processes.
- **Third-Party API Validation**: Sanitize and validate all data received from external APIs before processing.

## Incident Response Considerations

- Revoke compromised API keys and JWT tokens immediately upon breach detection.
- Enable enhanced logging and monitoring on affected API endpoints during investigation.
- Assess data exposure scope from BOLA or authentication bypass incidents.
- Deploy emergency rate limiting and IP blocking for active API abuse campaigns.
- Update API security testing in CI/CD pipeline based on incident root cause.

## Framework References

- OWASP API Security Top 10 (2023)
- OAuth 2.0 Authorization Framework
- OpenAPI Specification 3.0
- NIST SP 800-204 (Microservices Security)
