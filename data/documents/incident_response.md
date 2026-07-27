# Cybersecurity Incident Response (IR)

## 1. Introduction

**Incident Response (IR)** is a structured methodology for handling and managing security breaches or cyberattacks to minimize impact, reduce recovery time, and prevent future occurrences.

---

## 2. NIST IR Lifecycle (NIST SP 800-61 Rev. 2)

```
[ Preparation ] ──▶ [ Detection & Analysis ] ──▶ [ Containment, Eradication & Recovery ] ──▶ [ Post-Incident Activity ]
```

1. **Preparation**: Developing playbooks, configuring SIEM alerts, training CSIRT teams, and performing tabletop exercises.
2. **Detection & Analysis**: Triaging indicators of compromise (IOCs), correlating logs, and identifying threat scope.
3. **Containment**:
   - *Short-Term Containment*: Isolating infected hosts from the network, disabling compromised accounts.
   - *Long-Term Containment*: Applying temporary patches and issuing new access credentials.
4. **Eradication & Recovery**: Removing malware binaries, restoring clean backups, and validating system integrity before returning to production.
5. **Post-Incident Activity**: Conducting a "Lessons Learned" meeting, updating IR playbooks, and complying with legal disclosure mandates.

---

## 3. Digital Forensics & Evidence Handling

- **Order of Volatility**: Collect memory (RAM) first, followed by network state, disk images, and remote backups.
- **Chain of Custody**: Document all evidence acquisition dates, cryptographic hashes (SHA-256), and handler signatures to ensure court admissibility.
