# DevSecOps & Pipeline Security

## 1. Concept & Fundamentals

**DevSecOps** integrates security practices directly into every phase of the Software Development Life Cycle (SDLC), moving away from legacy perimeter security and manual end-of-cycle audits toward automated continuous security ("Shift Left").

---

## 2. CI/CD Security Automation Tools

```
[ Plan ] ──▶ [ Code (Secret Scan) ] ──▶ [ Build (SCA/SAST) ] ──▶ [ Test (DAST) ] ──▶ [ Deploy (IAC Scan) ] ──▶ [ Monitor ]
```

| Tool Category | Purpose | Examples |
| :--- | :--- | :--- |
| **Secret Scanning** | Prevents API keys, credentials, and private certs from entering git repositories. | GitGuardian, TruffleHog |
| **SAST (Static Analysis)** | Scans source code for security vulnerabilities without running the application. | SonarQube, Semgrep, Bandit |
| **SCA (Software Composition)** | Identifies known CVEs in open-source third-party dependencies and libraries. | Snyk, OWASP Dependency-Check |
| **DAST (Dynamic Analysis)** | Tests running web applications against dynamic attack vectors. | OWASP ZAP, Burp Suite |
| **IaC Scanning** | Validates Terraform, CloudFormation, and Ansible templates for cloud misconfigurations. | Checkov, tfsec |

---

## 3. CI/CD Pipeline Hardening Best Practices

- **Ephemeral Runner Environments**: Use isolated, single-use container runners for build jobs.
- **Signed Commits & Artifact Attestation**: Enforce GPG signed git commits and SLSA-compliant build provenance.
- **Principle of Least Privilege for Secrets**: Restrict CI/CD environment variables; inject short-lived OAuth tokens via HashiCorp Vault or OIDC instead of static credentials.
