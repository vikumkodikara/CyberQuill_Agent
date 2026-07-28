---
title: DevSecOps & Pipeline Security
categories: [Vulnerability Management, Cloud Security]
keywords: [DevSecOps, CI/CD, SAST, DAST, SCA, shift left, pipeline security]
frameworks: [OWASP DevSecOps Guideline, NIST SSDF, CIS Controls]
---

# DevSecOps & Pipeline Security

## Overview

DevSecOps integrates security practices into the software development lifecycle, embedding automated security testing into CI/CD pipelines. The shift-left approach identifies vulnerabilities early when they are cheapest to fix, reducing production security incidents and accelerating secure software delivery.

## Key Concepts & Attack Vectors

- **CI/CD Pipeline Compromise**: Attackers inject malicious code through compromised build servers, credentials, or dependency poisoning.
- **Secrets in Source Code**: Hardcoded API keys, passwords, and tokens committed to version control repositories.
- **Vulnerable Dependencies**: Third-party libraries with known CVEs introduced through supply chain attacks.
- **Insecure Container Images**: Base images with unpatched vulnerabilities deployed to production environments.
- **Insufficient Security Testing**: Missing SAST, DAST, and SCA scans allowing vulnerabilities to reach production.

## Detection & Indicators

| Tool Category | Purpose | Examples |
| :--- | :--- | :--- |
| **SAST** | Scans source code for vulnerabilities | SonarQube, Semgrep, Checkmarx |
| **DAST** | Tests running applications for flaws | OWASP ZAP, Burp Suite |
| **SCA** | Identifies vulnerable dependencies | Snyk, Dependabot, OWASP Dependency-Check |
| **Secret Scanning** | Detects credentials in code | GitGuardian, TruffleHog, Gitleaks |
| **Container Scanning** | Audits container images for CVEs | Trivy, Grype, Clair |

## Mitigation & Best Practices

- **Shift Left Security**: Integrate SAST and SCA into pull request workflows before code merges.
- **Immutable Infrastructure**: Deploy infrastructure as code with automated compliance scanning.
- **Secrets Management**: Use vault solutions (HashiCorp Vault, AWS Secrets Manager) instead of hardcoded credentials.
- **Signed Artifacts**: Sign container images and build artifacts to verify integrity in deployment pipelines.
- **Least Privilege CI/CD**: Restrict pipeline service account permissions to minimum required scope.

## Incident Response Considerations

- Halt all pipeline deployments immediately upon detecting compromised build artifacts.
- Rotate all secrets and credentials accessible from the compromised pipeline.
- Audit git history and dependency trees for malicious code injection points.
- Rebuild and re-sign all artifacts from known-good source commits.
- Update pipeline security controls and add detection rules for the attack vector used.

## Framework References

- OWASP DevSecOps Guideline
- NIST Secure Software Development Framework (SSDF)
- SLSA (Supply-chain Levels for Software Artifacts)
- CIS Control 16: Application Software Security
