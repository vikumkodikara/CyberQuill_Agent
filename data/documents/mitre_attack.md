---
title: MITRE ATT&CK Framework
categories: [Threat Intelligence, Malware]
keywords: [MITRE ATT&CK, tactics, techniques, procedures, TTPs, adversary, kill chain]
frameworks: [MITRE ATT&CK Enterprise, MITRE ATT&CK Mobile, MITRE D3FEND]
---

# MITRE ATT&CK Framework

## Overview

MITRE ATT&CK is a globally accessible knowledge base of adversary tactics and techniques based on real-world observations. It provides a common language for describing cyber attacks, enabling threat intelligence, detection engineering, and security assessment across enterprise, mobile, and ICS environments.

## Key Concepts & Attack Vectors

### Tactics (The "Why")
- **Reconnaissance**: Gathering information to plan future operations.
- **Initial Access**: Gaining entry via phishing, exploits, or supply chain compromise.
- **Execution**: Running adversary-controlled code on local or remote systems.
- **Persistence**: Maintaining foothold through registry keys, scheduled tasks, or implants.
- **Privilege Escalation**: Gaining higher-level permissions on the system.
- **Defense Evasion**: Avoiding detection through obfuscation and disabling security tools.
- **Credential Access**: Stealing credentials via keylogging, dumping, or brute force.
- **Discovery**: Learning about the internal network and environment.
- **Lateral Movement**: Moving through the environment using remote services and stolen credentials.
- **Collection**: Gathering data of interest for exfiltration.
- **Exfiltration**: Stealing data via C2 channels, cloud storage, or physical media.
- **Impact**: Disrupting availability through ransomware, data destruction, or service stop.

## Detection & Indicators

- Map SIEM and EDR detections to ATT&CK technique IDs for coverage gap analysis.
- Build detection rules targeting high-priority techniques for your threat model.
- Use ATT&CK Navigator to visualize defensive coverage across tactics.
- Correlate multiple technique detections to identify multi-stage attack campaigns.
- Monitor for techniques associated with known threat group profiles (APT29, FIN7, etc.).

## Mitigation & Best Practices

- **Detection Engineering**: Build detections mapped to ATT&CK techniques with tested fidelity.
- **Purple Team Exercises**: Simulate ATT&CK techniques to validate detection and response capabilities.
- **Threat-Informed Defense**: Prioritize controls based on techniques used by threat actors targeting your sector.
- **MITRE D3FEND**: Use the defensive countermeasure knowledge base to select appropriate mitigations.
- **ATT&CK-Based Reporting**: Structure incident reports and threat intelligence using ATT&CK terminology.

## Incident Response Considerations

- Map observed attacker behavior to ATT&CK techniques during active incident investigation.
- Use technique mapping to predict adversary next steps and proactively deploy countermeasures.
- Document full attack chain using ATT&CK for post-incident reporting and intelligence sharing.
- Identify detection gaps revealed by the incident and prioritize new rule development.
- Share ATT&CK-mapped IOCs and TTPs with information sharing communities.

## Framework References

- MITRE ATT&CK Enterprise Matrix
- MITRE ATT&CK for Mobile and ICS
- MITRE D3FEND Knowledge Graph
- MITRE ATT&CK Evaluations
