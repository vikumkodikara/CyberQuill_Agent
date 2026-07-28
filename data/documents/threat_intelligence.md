---
title: Cyber Threat Intelligence
categories: [Threat Intelligence, Malware]
keywords: [CTI, STIX, TAXII, IOC, threat actors, diamond model, TTPs]
frameworks: [STIX 2.1, TAXII 2.1, MITRE ATT&CK, Diamond Model]
---

# Cyber Threat Intelligence (CTI)

## Overview

Cyber Threat Intelligence (CTI) is evidence-based knowledge—including context, mechanisms, indicators, implications, and actionable advice—about existing or emerging hazards to assets. Effective CTI programs transform raw security data into prioritized, actionable intelligence that enables proactive defense, informed risk decisions, and faster incident response.

## Key Concepts & Attack Vectors

1. **Strategic Intelligence** — High-level analysis for executive decision-makers covering geopolitical risks, threat actor motivation, and budget planning.
2. **Operational Intelligence** — Insights into specific campaign tactics, capabilities, and upcoming threat actor operations.
3. **Tactical Intelligence** — Technical details on threat actor TTPs mapped to MITRE ATT&CK techniques and procedures.
4. **Technical Intelligence** — Short-lived Indicators of Compromise (IOCs): IP addresses, file hashes, malicious domains, and registry keys.
5. **Threat Actor Lifecycle** — Reconnaissance, weaponization, delivery, exploitation, installation, command and control, and actions on objectives.

## Detection & Indicators

- Correlate IOCs (hashes, IPs, domains) against threat feeds and internal telemetry using STIX/TAXII integrations.
- Monitor for TTP patterns matching known adversary campaigns in SIEM and EDR platforms.
- Track dark web and breach forum mentions of organizational assets or credentials.
- Identify infrastructure overlaps between campaigns using the Diamond Model (adversary, capability, infrastructure, victim).
- Detect anomalous behavior consistent with known APT group playbooks.

## Mitigation & Best Practices

- **STIX/TAXII Integration**: Automate ingestion and sharing of threat intelligence across security tools via standardized formats.
- **Intelligence-Driven Defense**: Prioritize patching and monitoring based on threat actor targeting of your industry vertical.
- **IOC Lifecycle Management**: Expire stale indicators promptly; technical intelligence has a short half-life.
- **Threat Hunting**: Proactively search for TTPs rather than relying solely on signature-based detection.
- **Information Sharing**: Participate in ISACs and industry sharing groups for collective defense.

## Incident Response Considerations

- Enrich incident data with CTI context to attribute attacks and predict adversary next steps.
- Block known malicious infrastructure identified in active campaigns during containment.
- Share anonymized indicators with trusted partners and government agencies.
- Update detection rules based on newly discovered TTPs from the incident.
- Feed lessons learned back into the intelligence cycle for continuous improvement.

## Framework References

- STIX 2.1 (Structured Threat Information eXpression)
- TAXII 2.1 (Trusted Automated eXchange of Intelligence Information)
- MITRE ATT&CK Framework for TTP mapping
- Diamond Model of Intrusion Analysis
