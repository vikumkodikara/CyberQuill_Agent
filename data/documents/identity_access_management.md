# Identity & Access Management (IAM)

## 1. Executive Summary

**Identity and Access Management (IAM)** is the foundational security discipline that ensures the right identities (users, services, devices) access the right resources for legitimate reasons under strict policy governance.

---

## 2. Federation Protocols & Standards

- **OAuth 2.0**: An open authorization framework enabling third-party applications to obtain limited access to HTTP services via access tokens.
- **OpenID Connect (OIDC)**: An identity layer built on top of OAuth 2.0 that provides user authentication and ID tokens (`JWT`).
- **SAML 2.0**: XML-based standard for exchanging authentication and authorization data between an Identity Provider (IdP) and a Service Provider (SP), heavily used in enterprise SSO.

---

## 3. Access Control Paradigms

| Control Model | Mechanism | Best Use Case |
| :--- | :--- | :--- |
| **RBAC (Role-Based)** | Grants permissions based on pre-defined job roles (e.g., Admin, Analyst, Auditor). | Static enterprise organizations |
| **ABAC (Attribute-Based)** | Evaluates dynamic attributes (user role, IP location, time of day, device trust). | Granular Zero Trust policies |
| **PAM (Privileged Access)** | Manages, monitors, and audits elevated accounts (e.g., root, domain admin). | High-security infrastructure access |

---

## 4. Multi-Factor Authentication (MFA) Hierarchy

1. **Phishing-Resistant MFA (Strongest)**: FIDO2 / WebAuthn hardware security keys, PKI Smart Cards.
2. **Time-Based One-Time Passwords (TOTP)**: Authenticator apps (Google/Microsoft Authenticator).
3. **SMS / Voice OTP (Weakest)**: Vulnerable to SIM swapping, SS7 interception, and AiTM phishing.
