---
title: Phishing & Social Engineering
categories: [Malware, Data Breach]
keywords: [phishing, BEC, spear phishing, SPF, DKIM, DMARC, social engineering, AiTM]
frameworks: [NIST SP 800-177, CIS Controls, MITRE ATT&CK]
---

# Phishing & Social Engineering

## Overview

Phishing and social engineering attacks manipulate human psychology to trick victims into revealing credentials, transferring funds, or executing malicious software. These attacks remain the most common initial access vector for ransomware, business email compromise (BEC), and data breaches across all industry sectors.

## Key Concepts & Attack Vectors

- **Mass Phishing**: Broad email campaigns targeting many recipients with generic lures.
- **Spear Phishing**: Targeted attacks against specific individuals using personalized content.
- **Business Email Compromise (BEC)**: Impersonating executives or vendors to authorize fraudulent wire transfers.
- **Adversary-in-the-Middle (AiTM)**: Proxy-based phishing that captures session tokens even with MFA enabled.
- **Vishing & Smishing**: Voice and SMS-based social engineering attacks.

## Detection & Indicators

- Email security gateways flagging suspicious sender domains, spoofed headers, and malicious attachments.
- DMARC failure reports indicating domain spoofing attempts against organizational domains.
- User-reported suspicious emails through phishing reporting buttons.
- Anomalous login patterns following credential submission on phishing pages.
- Detection of newly registered lookalike domains mimicking corporate brands.

## Mitigation & Best Practices

- **Email Authentication**: Implement SPF, DKIM, and DMARC with p=reject policy for all domains.
- **Security Awareness Training**: Conduct regular phishing simulations and targeted training for high-risk users.
- **Anti-Phishing Technology**: Deploy email security gateways with URL rewriting and attachment sandboxing.
- **MFA with Phishing Resistance**: Use FIDO2/WebAuthn hardware keys instead of SMS or TOTP for critical accounts.
- **Payment Verification Procedures**: Require out-of-band confirmation for wire transfers and vendor changes.

## Incident Response Considerations

- Reset credentials for all users who submitted data on phishing pages.
- Revoke active sessions and tokens for compromised accounts immediately.
- Block phishing URLs and domains at email gateway, DNS, and web proxy layers.
- Investigate BEC incidents for unauthorized financial transactions and initiate recovery.
- Report phishing campaigns to anti-phishing organizations and domain registrars.

## Framework References

- NIST SP 800-177 (Trustworthy Email)
- MITRE ATT&CK Initial Access Techniques (T1566)
- CIS Control 14: Security Awareness and Skills Training
- Anti-Phishing Working Group (APWG) Reporting
