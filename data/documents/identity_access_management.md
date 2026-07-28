---
title: Identity & Access Management
categories: [Data Breach, Cloud Security]
keywords: [IAM, OAuth2, OIDC, SAML, MFA, SSO, privileged access, RBAC]
frameworks: [NIST SP 800-63, OAuth 2.0, OIDC, SAML 2.0, CIS Controls]
---

# Identity & Access Management (IAM)

## Overview

Identity and Access Management (IAM) governs how users, services, and devices authenticate and authorize access to organizational resources. Weak IAM controls are a leading cause of data breaches, enabling account takeover, privilege escalation, and unauthorized data access across cloud and on-premises environments.

## Key Concepts & Attack Vectors

- **Broken Authentication**: Weak passwords, missing MFA, and session management flaws enabling credential theft.
- **Privilege Escalation**: Exploiting misconfigured roles, group memberships, or IAM policies to gain administrative access.
- **OAuth/OIDC Misconfiguration**: Insecure redirect URIs, overly broad scopes, and token leakage in single sign-on flows.
- **SAML Assertion Forgery**: XML signature wrapping attacks and certificate validation bypasses in federation.
- **Credential Stuffing**: Automated login attempts using breached username/password pairs from third-party leaks.

## Detection & Indicators

- Monitor for impossible travel logins and authentication from anomalous geographic locations.
- Alert on privilege escalation events, new admin role assignments, and policy modifications.
- Detect brute-force login attempts and credential stuffing patterns in authentication logs.
- Track dormant account reactivation and service account usage outside business hours.
- Identify OAuth consent grants to suspicious third-party applications.

## Mitigation & Best Practices

- **Multi-Factor Authentication**: Enforce phishing-resistant MFA (FIDO2/WebAuthn) on all privileged and remote access.
- **Principle of Least Privilege**: Grant minimum permissions required; use just-in-time (JIT) access for admin tasks.
- **Role-Based Access Control**: Implement RBAC with regular access reviews and automated deprovisioning.
- **Single Sign-On**: Centralize authentication via OIDC/SAML with conditional access policies.
- **Privileged Access Management**: Vault admin credentials, enforce session recording, and require approval workflows.

## Incident Response Considerations

- Disable compromised accounts and revoke all active sessions and tokens immediately.
- Reset credentials for all accounts showing signs of unauthorized access.
- Review IAM audit logs to determine scope of privilege escalation and data accessed.
- Rotate service account keys and API tokens used by compromised identities.
- Implement emergency access procedures while restoring normal IAM operations.

## Framework References

- NIST SP 800-63 (Digital Identity Guidelines)
- OAuth 2.0 Authorization Framework (RFC 6749)
- OpenID Connect Core 1.0
- SAML 2.0 Web Browser SSO Profile
- CIS Control 5: Account Management
