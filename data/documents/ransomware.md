# Ransomware: Encryption Mechanisms, Attack Vectors, and Defense Strategies

## Overview
Ransomware is a type of malicious software that encrypts a victim's files or locks their systems, demanding payment (usually in cryptocurrency) for the decryption key. Ransomware has evolved from simple screen lockers to sophisticated double-extortion and triple-extortion schemes that threaten to leak stolen data, launch DDoS attacks, or contact the victim's customers and partners.

## How Ransomware Encryption Works

### Symmetric Encryption Phase
Ransomware typically uses a hybrid encryption approach for speed and security. The malware generates a unique AES-256 symmetric key for each victim (or per file). AES (Advanced Encryption Standard) in CBC or CTR mode encrypts files rapidly, processing gigabytes of data in minutes. Each file is encrypted with the symmetric key, and the original file is overwritten or deleted. Some variants encrypt only the first portion of large files to speed up the process while rendering them unusable.

### Asymmetric Encryption Phase
The symmetric key itself is encrypted using RSA-2048 or RSA-4096 public key encryption. The attacker's public key is embedded in the ransomware binary. The victim's unique AES key is encrypted with this public key, making it recoverable only with the attacker's private key. The encrypted AES key is stored alongside the encrypted files or sent to the attacker's command and control server. This hybrid approach combines the speed of symmetric encryption with the security of asymmetric encryption.

### File Targeting and Encryption Process
Ransomware follows a systematic process to maximize damage. First, it enumerates all drives including mapped network drives and removable media. Then it identifies target file extensions such as documents (.docx, .pdf, .xlsx), databases (.sql, .mdb), images (.jpg, .png), source code (.py, .java, .cpp), and virtual machine files (.vmdk, .vhd). It skips system files to keep the machine bootable so the ransom note can be displayed. Files are encrypted and typically renamed with a new extension (e.g., .locked, .encrypted, .ryuk). Volume shadow copies are deleted using vssadmin or wmic to prevent recovery.

## Notable Ransomware Families

### WannaCry (2017)
WannaCry exploited the EternalBlue SMB vulnerability (MS17-010) to spread as a worm across networks. It used AES-128-CBC for file encryption and RSA-2048 for key encryption. The attack affected over 200,000 systems in 150 countries, including the UK National Health Service. A kill switch domain was discovered that halted the spread.

### REvil/Sodinokibi
REvil operated as Ransomware-as-a-Service (RaaS), allowing affiliates to deploy the ransomware in exchange for a percentage of the ransom. It used Salsa20 for file encryption and curve25519 for key exchange. REvil pioneered the double-extortion model, threatening to publish stolen data on a leak site if the ransom was not paid.

### LockBit
LockBit is one of the fastest encrypting ransomware families, using multi-threaded encryption with intermittent encryption (encrypting only portions of each file). It uses AES-256 in CTR mode with RSA-2048 for key wrapping. LockBit operates a sophisticated RaaS program and has a bug bounty program for improving its malware.

### BlackCat/ALPHV
BlackCat is the first major ransomware written in Rust, making it cross-platform (Windows, Linux, VMware ESXi). It uses AES-256 in CTR mode or ChaCha20 with RSA for key encryption. Its Rust-based architecture makes analysis and detection more difficult.

## Ransomware Attack Lifecycle

### Initial Access
Attackers gain entry through phishing emails with malicious attachments or links, exploiting public-facing vulnerabilities (VPN, RDP, web applications), compromised credentials purchased from initial access brokers, supply chain attacks through trusted software updates, and drive-by downloads from compromised websites.

### Lateral Movement and Privilege Escalation
After initial access, attackers move laterally through the network. They harvest credentials using tools like Mimikatz, exploit Active Directory vulnerabilities (Zerologon, PrintNightmare), use remote administration tools (PsExec, PowerShell remoting), escalate to domain administrator privileges, and map the network to identify critical systems and backup infrastructure.

### Data Exfiltration (Double Extortion)
Before encrypting, attackers steal sensitive data. They identify and collect valuable data (financial records, intellectual property, personal data), exfiltrate data using tools like Rclone, MEGAsync, or custom exfiltration tools, transfer data to attacker-controlled infrastructure, and use the stolen data as additional leverage for ransom payment.

### Deployment and Encryption
The final stage involves deploying ransomware across the network. Attackers disable security tools and endpoint detection, delete backups and shadow copies, deploy ransomware through Group Policy, PsExec, or scheduled tasks, trigger encryption simultaneously across all compromised systems, and display ransom notes with payment instructions.

## Defense Strategies

### Prevention
Implement email security gateways with attachment sandboxing, keep all systems patched and updated especially internet-facing systems, disable or restrict RDP and implement VPN with MFA, use application whitelisting to prevent unauthorized executables, implement network segmentation to limit lateral movement, and conduct regular security awareness training focused on phishing.

### Detection
Deploy endpoint detection and response (EDR) solutions on all endpoints, monitor for indicators of compromise such as mass file modifications, unusual process behavior, and shadow copy deletion. Implement behavioral detection rules for ransomware patterns, use network detection tools to identify C2 communications and data exfiltration, and monitor for abnormal authentication patterns and privilege escalation.

### Backup and Recovery
Maintain the 3-2-1 backup rule: three copies of data on two different media types with one copy offsite. Test backup restoration procedures regularly, implement immutable backups that cannot be modified or deleted, use air-gapped backup solutions for critical data, maintain offline backup copies, and ensure backup systems require separate authentication credentials.

### Incident Response
Develop and test a ransomware-specific incident response plan, isolate infected systems immediately to prevent spread, preserve forensic evidence before rebuilding systems, engage law enforcement and report the incident, evaluate decryption options (free decryptors available for some families at No More Ransom project), and avoid paying the ransom when possible as payment does not guarantee data recovery and funds criminal operations.
