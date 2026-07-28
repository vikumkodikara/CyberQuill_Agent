---
title: Ransomware Encryption and Defense Strategies
categories: [Malware, Data Breach]
keywords: [ransomware, encryption, double extortion, RaaS, backup, LockBit, REvil]
frameworks: [NIST SP 800-61, CISA Ransomware Guide, MITRE ATT&CK]
---

# Ransomware: Encryption Mechanisms, Attack Vectors, and Defense Strategies

## Overview

Ransomware is malicious software that encrypts a victim's files or locks their systems, demanding payment (usually cryptocurrency) for the decryption key. Modern ransomware has evolved from simple screen lockers to sophisticated double-extortion and triple-extortion schemes that threaten to leak stolen data, launch DDoS attacks, or contact customers and partners.

## Key Concepts & Attack Vectors

- **Hybrid Encryption**: AES-256 symmetric key per victim for fast file encryption, wrapped with RSA-2048/4096 public key.
- **Double Extortion**: Data exfiltration before encryption, using stolen data as additional ransom leverage.
- **Ransomware-as-a-Service (RaaS)**: REvil, LockBit, and BlackCat operate affiliate programs distributing malware for profit share.
- **Attack Lifecycle**: Initial access (phishing, RDP, VPN exploits) → lateral movement → data exfiltration → encryption deployment.
- **Notable Families**: WannaCry (EternalBlue worm), REvil (Salsa20), LockBit (fastest encryption), BlackCat (Rust-based, cross-platform).

## Detection & Indicators

- Mass file modification events and unusual file extension changes (.locked, .encrypted, .ryuk).
- Shadow copy deletion via vssadmin or wmic commands.
- EDR alerts for suspicious process behavior and security tool disabling.
- Network detection of C2 communications and data exfiltration (Rclone, MEGAsync).
- Abnormal authentication patterns and privilege escalation before encryption trigger.

## Mitigation & Best Practices

- **3-2-1 Backup Rule**: Three copies on two media types with one offsite; test restoration regularly.
- **Immutable Backups**: Use air-gapped or write-once backup solutions ransomware cannot modify.
- **Network Segmentation**: Limit lateral movement between network segments.
- **EDR Deployment**: Behavioral detection on all endpoints for ransomware patterns.
- **Patch Management**: Keep internet-facing systems patched, especially VPN and RDP services.

## Incident Response Considerations

- Isolate infected systems immediately to prevent spread across the network.
- Preserve forensic evidence before rebuilding systems.
- Do not pay ransom when possible — payment does not guarantee recovery and funds criminal operations.
- Check No More Ransom project for free decryptors available for some families.
- Engage law enforcement and report the incident; preserve ransom notes and wallet addresses.

## Framework References

- CISA Stop Ransomware Guide
- NIST SP 800-61 (Incident Response)
- MITRE ATT&CK Impact Techniques (T1486 Data Encrypted for Impact)
- No More Ransom Project (nomoreransom.org)
