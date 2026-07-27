# Phishing & Social Engineering Vectors

## 1. Executive Summary

**Social Engineering** encompasses psychological manipulation techniques used by attackers to trick individuals into disclosing confidential information, executing malware, or transferring funds.

---

## 2. Key Attack Categories

- **Spear Phishing**: Targeted phishing attacks tailored to specific individuals or organizations using OSINT reconnaissance.
- **Business Email Compromise (BEC)**: Fraudulent emails impersonating executives, legal counsel, or vendors to authorize wire transfers or credential sharing.
- **Adversary-in-the-Middle (AiTM) Phishing**: Reverse-proxy frameworks (e.g., Evilginx) that capture session cookies and bypass standard TOTP MFA.
- **MFA Fatigue / Push Spamming**: Bombarding victims with constant push notifications until they approve out of frustration or confusion.
- **Vishing & Smishing**: Voice-based (Vishing) and SMS-based (Smishing) lure vectors, increasingly augmented by AI voice cloning.

---

## 3. Technical Defenses & Email Authentication Protocols

### A. Email Authentication Standards
- **SPF (Sender Policy Framework)**: Specifies which IP addresses are authorized to send email on behalf of a domain.
- **DKIM (DomainKeys Identified Mail)**: Adds a cryptographic digital signature to outgoing email headers.
- **DMARC (Domain-based Message Authentication, Reporting, and Conformance)**: Enforces policies (`p=reject` or `p=quarantine`) for emails failing SPF or DKIM checks.

### B. Modern Phishing Defenses
- **FIDO2 / WebAuthn Hardware Keys**: Deploy phishing-resistant MFA (e.g., YubiKeys, Passkeys) to neutralize AiTM attacks.
- **Automated Sandbox Email Gateway**: Analyze incoming attachments and URLs in an isolated sandbox before delivery to inbox.
