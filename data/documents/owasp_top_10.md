# OWASP Top 10 Web Application Security Risks (2021)

## A01:2021 – Broken Access Control
Access control enforces policy such that users cannot act outside of their intended permissions. Failures typically lead to unauthorized information disclosure, modification, or destruction of data, or performing a business function outside the user's limits. Common vulnerabilities include violation of the principle of least privilege, bypassing access control checks by modifying the URL, internal application state, or the HTML page, permitting viewing or editing someone else's account, elevation of privilege, and CORS misconfiguration.

## A02:2021 – Cryptographic Failures
Previously known as Sensitive Data Exposure, this category focuses on failures related to cryptography which often lead to exposure of sensitive data. Notable CWEs include use of hard-coded password, broken or risky crypto algorithm, and insufficient entropy. Organizations should classify data processed, stored, or transmitted by an application. Identify which data is sensitive according to privacy laws, regulatory requirements, or business needs. Ensure that sensitive data is encrypted at rest and in transit.

## A03:2021 – Injection
An application is vulnerable to injection when user-supplied data is not validated, filtered, or sanitized by the application. SQL injection, NoSQL injection, OS command injection, LDAP injection, and Cross-Site Scripting (XSS) are common injection flaws. Preventive measures include using safe APIs which avoid using the interpreter entirely, using positive server-side input validation, and escaping special characters.

## A04:2021 – Insecure Design
Insecure design is a broad category representing different weaknesses, expressed as missing or ineffective control design. An insecure design cannot be fixed by a perfect implementation as by definition, needed security controls were never created to defend against specific attacks. Organizations should establish and use a secure development lifecycle with AppSec professionals to help evaluate and design security and privacy-related controls.

## A05:2021 – Security Misconfiguration
The application might be vulnerable if the application is missing appropriate security hardening across any part of the application stack or improperly configured permissions on cloud services. Default accounts and their passwords are still enabled and unchanged. Error handling reveals stack traces or other overly informative error messages to users. For upgraded systems, the latest security features are disabled or not configured securely.

## A06:2021 – Vulnerable and Outdated Components
Components such as libraries, frameworks, and other software modules run with the same privileges as the application. If a vulnerable component is exploited, such an attack can facilitate serious data loss or server takeover. Applications and APIs using components with known vulnerabilities may undermine application defenses and enable various attacks and impacts. Organizations should remove unused dependencies, unnecessary features, components, files, and documentation.

## A07:2021 – Identification and Authentication Failures
Confirmation of the user's identity, authentication, and session management is critical to protect against authentication-related attacks. Application security weaknesses include permitting brute force or other automated attacks, permitting default, weak, or well-known passwords, using weak or ineffective credential recovery and forgot-password processes, and missing or ineffective multi-factor authentication.

## A08:2021 – Software and Data Integrity Failures
Software and data integrity failures relate to code and infrastructure that does not protect against integrity violations. An example of this is where an application relies upon plugins, libraries, or modules from untrusted sources, repositories, and content delivery networks (CDNs). An insecure CI/CD pipeline can introduce the potential for unauthorized access, malicious code, or system compromise.

## A09:2021 – Security Logging and Monitoring Failures
This category is to help detect, escalate, and respond to active breaches. Without logging and monitoring, breaches cannot be detected. Insufficient logging, detection, monitoring, and active response occurs any time auditable events such as logins, failed logins, and high-value transactions are not logged, warnings and errors generate no or inadequate log messages, and logs are only stored locally.

## A10:2021 – Server-Side Request Forgery (SSRF)
SSRF flaws occur whenever a web application is fetching a remote resource without validating the user-supplied URL. It allows an attacker to coerce the application to send a crafted request to an unexpected destination, even when protected by a firewall, VPN, or another type of network access control list (ACL). SSRF attacks can be used to scan internal networks, access internal services, and read local files.
