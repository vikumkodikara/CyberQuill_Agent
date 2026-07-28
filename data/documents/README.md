# CyberQuill RAG Knowledge Base Documents (20 Files)

This directory contains the 20 curated Markdown knowledge base documents used by the CyberQuill RAG Agent (`agents/rag.py`) and indexed into ChromaDB.

## Frontmatter Schema

Each knowledge file includes YAML frontmatter for metadata-driven retrieval:

```yaml
---
title: <Topic Name>
categories: [CyberQuill category tags]
keywords: [search terms for retrieval]
frameworks: [OWASP, NIST, MITRE, etc.]
---
```

**Note:** `README.md` is excluded from indexing. Files without a `title` in frontmatter are also skipped.

## Section Template

All knowledge files follow this structure:

1. **Overview** — Topic introduction and significance
2. **Key Concepts & Attack Vectors** — Core threats and techniques
3. **Detection & Indicators** — How to identify attacks and compromise
4. **Mitigation & Best Practices** — Actionable defensive controls
5. **Incident Response Considerations** — IR-specific guidance
6. **Framework References** — Standards and frameworks cited

## Knowledge Base Files Index

1. `ai_security.md` — AI & LLM Security (OWASP LLM Top 10, Prompt Injection)
2. `api_security.md` — API Security & OWASP API Top 10
3. `cloud_security.md` — Cloud Infrastructure & Misconfiguration Security
4. `container_k8s_security.md` — Docker & Kubernetes Security
5. `cryptography_pki.md` — Cryptography, PKI, TLS, Post-Quantum
6. `ddos_mitigation.md` — DDoS Attack Vectors & Mitigation
7. `devsecops.md` — DevSecOps, CI/CD, SAST/DAST/SCA
8. `identity_access_management.md` — IAM, OAuth2, OIDC, SAML, MFA
9. `incident_response.md` — NIST Incident Response Lifecycle
10. `iot_firmware_security.md` — IoT, Firmware, Embedded Systems
11. `malware_analysis.md` — Malware RE, Sandbox Analysis, YARA
12. `mitre_attack.md` — MITRE ATT&CK Tactics & Techniques
13. `nist_csf.md` — NIST Cybersecurity Framework 2.0
14. `owasp_top_10.md` — OWASP Top 10 Web Vulnerabilities
15. `phishing_social_engineering.md` — Phishing, BEC, SPF/DKIM/DMARC
16. `ransomware.md` — Ransomware Mitigation & Disaster Recovery
17. `sql_injection.md` — SQL Injection Prevention & Remediation
18. `threat_intelligence.md` — CTI, STIX/TAXII, Diamond Model
19. `zero_day_exploits.md` — Zero-Day Lifecycle & Virtual Patching
20. `zero_trust_architecture.md` — Zero Trust (NIST SP 800-207)

## Category-to-Source Mapping

The RAG agent uses `CATEGORY_SOURCE_MAP` in `agents/rag.py` to boost retrieval from relevant sources based on article classification.

## Rebuilding the Index

After modifying knowledge files, rebuild the ChromaDB index:

```python
from agents.rag import build_knowledge_base
build_knowledge_base()
```

Or use the **Rebuild Knowledge Base** button on the RAG Testing page.
