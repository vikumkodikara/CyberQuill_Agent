# MITRE ATT&CK Framework Summary

## Overview
MITRE ATT&CK (Adversarial Tactics, Techniques, and Common Knowledge) is a globally-accessible knowledge base of adversary tactics and techniques based on real-world observations. The ATT&CK knowledge base is used as a foundation for the development of specific threat models and methodologies in the private sector, government, and the cybersecurity product and service community.

## Tactics (The "Why")
Tactics represent the adversary's tactical objective or the reason for performing an action.

### Reconnaissance (TA0043)
The adversary is trying to gather information they can use to plan future operations. Techniques include active scanning, gathering victim host information, gathering victim identity information, gathering victim network information, phishing for information, and searching open technical databases and websites.

### Resource Development (TA0042)
The adversary is trying to establish resources they can use to support operations. This includes acquiring infrastructure such as domains, servers, and web services, compromising accounts, developing capabilities like malware and exploits, and establishing accounts on services.

### Initial Access (TA0001)
The adversary is trying to get into your network. Techniques include drive-by compromise, exploiting public-facing applications, external remote services, hardware additions, phishing, replication through removable media, supply chain compromise, trusted relationship exploitation, and valid accounts abuse.

### Execution (TA0002)
The adversary is trying to run malicious code. Techniques include command and scripting interpreter abuse, container administration commands, exploitation for client execution, inter-process communication abuse, native API abuse, scheduled task/job creation, shared modules, software deployment tools, system services manipulation, user execution, and Windows Management Instrumentation.

### Persistence (TA0003)
The adversary is trying to maintain their foothold. Techniques include account manipulation, BITS jobs, boot or logon autostart execution, boot or logon initialization scripts, browser extensions, compromise client software binary, create account, create or modify system process, event triggered execution, external remote services, hijack execution flow, implant internal image, modify authentication process, office application startup, pre-OS boot, scheduled task/job, server software component, and traffic signaling.

### Privilege Escalation (TA0004)
The adversary is trying to gain higher-level permissions. Techniques include abuse elevation control mechanism, access token manipulation, boot or logon autostart execution, boot or logon initialization scripts, create or modify system process, domain policy modification, escape to host, event triggered execution, exploitation for privilege escalation, hijack execution flow, process injection, scheduled task/job, and valid accounts.

### Defense Evasion (TA0005)
The adversary is trying to avoid being detected. Techniques include abuse elevation control mechanism, access token manipulation, BITS jobs, build image on host, deobfuscate/decode files or information, deploy container, direct volume access, domain policy modification, execution guardrails, exploitation for defense evasion, file and directory permissions modification, hide artifacts, hijack execution flow, impair defenses, indicator removal, indirect command execution, masquerading, modify authentication process, modify cloud compute infrastructure, modify registry, modify system image, network boundary bridging, obfuscated files or information, plist file modification, pre-OS boot, process injection, reflective code loading, rogue domain controller, rootkit, subvert trust controls, system binary proxy execution, system script proxy execution, template injection, traffic signaling, trusted developer utilities proxy execution, unused/unsupported cloud regions, use alternate authentication material, valid accounts, virtualization/sandbox evasion, weaken encryption, and XSL script processing.

### Credential Access (TA0006)
The adversary is trying to steal account names and passwords. Techniques include adversary-in-the-middle attacks, brute force, credentials from password stores, exploitation for credential access, forced authentication, forge web credentials, input capture, modify authentication process, multi-factor authentication interception, multi-factor authentication request generation, network sniffing, OS credential dumping, steal application access token, steal or forge Kerberos tickets, steal web session cookie, and unsecured credentials.

### Discovery (TA0007)
The adversary is trying to figure out your environment. Techniques include account discovery, application window discovery, browser bookmark discovery, cloud infrastructure discovery, cloud service dashboard, cloud service discovery, cloud storage object discovery, container and resource discovery, domain trust discovery, file and directory discovery, group policy discovery, network service discovery, network share discovery, network sniffing, password policy discovery, peripheral device discovery, permission groups discovery, process discovery, query registry, remote system discovery, software discovery, system information discovery, system location discovery, system network configuration discovery, system network connections discovery, system owner/user discovery, system service discovery, system time discovery, and virtualization/sandbox evasion.

### Lateral Movement (TA0008)
The adversary is trying to move through your environment. Techniques include exploitation of remote services, internal spearphishing, lateral tool transfer, remote service session hijacking, remote services, software deployment tools, taint shared content, and use alternate authentication material.

### Collection (TA0009)
The adversary is trying to gather data of interest to their goal. Techniques include adversary-in-the-middle, archive collected data, audio capture, automated collection, browser session hijacking, clipboard data, data from cloud storage object, data from configuration repository, data from information repositories, data from local system, data from network shared drive, data from removable media, data staged, email collection, input capture, screen capture, and video capture.

### Command and Control (TA0011)
The adversary is trying to communicate with compromised systems to control them. Techniques include application layer protocol, communication through removable media, data encoding, data obfuscation, dynamic resolution, encrypted channel, fallback channels, ingress tool transfer, multi-stage channels, non-application layer protocol, non-standard port, protocol tunneling, proxy, remote access software, traffic signaling, and web service.

### Exfiltration (TA0010)
The adversary is trying to steal data. Techniques include automated exfiltration, data transfer size limits, exfiltration over alternative protocol, exfiltration over C2 channel, exfiltration over other network medium, exfiltration over physical medium, exfiltration over web service, scheduled transfer, and transfer data to cloud account.

### Impact (TA0040)
The adversary is trying to manipulate, interrupt, or destroy your systems and data. Techniques include account access removal, data destruction, data encrypted for impact (ransomware), data manipulation, defacement, disk wipe, endpoint denial of service, firmware corruption, inhibit system recovery, network denial of service, resource hijacking, service stop, and system shutdown/reboot.
