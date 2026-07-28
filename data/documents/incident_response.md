---
title: Cybersecurity Incident Response
categories: [Data Breach, Threat Intelligence]
keywords: [incident response, forensics, containment, NIST IR, breach, SOC]
frameworks: [NIST SP 800-61, SANS IR, MITRE ATT&CK]
---

# Cybersecurity Incident Response

## Overview

Incident response is the organized approach to addressing and managing the aftermath of a security breach or cyber attack. A well-defined incident response plan minimizes damage, reduces recovery time, and ensures regulatory compliance. The NIST incident response lifecycle provides the standard framework for preparation through post-incident activities.

## Key Concepts & Attack Vectors

- **Preparation**: Establishing IR team, tools, communication plans, and playbooks before incidents occur.
- **Detection & Analysis**: Identifying security events, validating incidents, and determining scope and severity.
- **Containment**: Short-term isolation and long-term containment to prevent further damage.
- **Eradication**: Removing threat actor presence, malware, and unauthorized access from affected systems.
- **Recovery**: Restoring systems to normal operations and verifying security before returning to production.
- **Post-Incident Activity**: Lessons learned, evidence preservation, and process improvements.

## Detection & Indicators

- SIEM alerts correlating multiple suspicious events into incident-worthy patterns.
- EDR detections of malware execution, lateral movement, and data exfiltration.
- User reports of phishing, ransomware notes, or unauthorized account activity.
- Network monitoring for C2 beaconing, unusual DNS queries, and large outbound transfers.
- Threat intelligence matching internal IOCs to known active campaigns.

## Mitigation & Best Practices

- **Incident Response Plan**: Maintain documented, tested IR plans with defined roles and escalation procedures.
- **Digital Forensics Readiness**: Preserve evidence using write-blockers, memory captures, and chain of custody procedures.
- **Communication Protocols**: Establish internal and external communication templates for stakeholders and regulators.
- **Tabletop Exercises**: Conduct regular IR simulations to test team readiness and playbook effectiveness.
- **Automated Playbooks**: Implement SOAR playbooks for common incident types (phishing, malware, data breach).

## Incident Response Considerations

- Activate IR team and establish incident commander within 15 minutes of confirmed breach.
- Preserve forensic evidence before remediation actions destroy critical artifacts.
- Engage legal counsel early for regulatory notification requirements (GDPR 72-hour rule).
- Document all actions taken with timestamps for post-incident review and compliance.
- Conduct blameless post-mortem within 5 business days of incident closure.

## Framework References

- NIST SP 800-61 Rev. 2 (Computer Security Incident Handling Guide)
- SANS Incident Handler's Handbook
- MITRE ATT&CK for threat mapping during analysis
- ISO/IEC 27035 (Information Security Incident Management)
