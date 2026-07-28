---
title: Distributed Denial of Service & Mitigation
categories: [Vulnerability Management, Malware]
keywords: [DDoS, volumetric attack, SYN flood, Layer 7, botnet, scrubbing]
frameworks: [NIST SP 800-61, OWASP, CIS Controls]
---

# Distributed Denial of Service (DDoS) & Mitigation

## Overview

A Distributed Denial of Service (DDoS) attack attempts to exhaust the bandwidth, computing power, or connection pools of a target system by flooding it with traffic originating from a botnet of compromised devices. Modern DDoS attacks combine volumetric, protocol, and application-layer techniques to overwhelm defenses and cause service outages.

## Key Concepts & Attack Vectors

- **Volumetric Attacks (Layer 3/4)**: Saturation of internet bandwidth using massive traffic volumes. UDP amplification abuses open NTP, DNS, or Memcached servers to multiply request sizes toward a spoofed target IP.
- **Protocol Attacks (Layer 3/4)**: Consuming infrastructure state table limits in firewalls and load balancers. SYN floods send half-open TCP connection requests until SYN queue capacity is breached.
- **Application Layer Attacks (Layer 7)**: Targeting specific web applications or database queries to exhaust CPU and memory. HTTP GET/POST floods send complex, resource-intensive requests.
- **Botnet Infrastructure**: Compromised IoT devices, servers, and workstations coordinated via command-and-control networks to generate attack traffic.

## Detection & Indicators

- Monitor bandwidth utilization spikes exceeding baseline thresholds by 3x or more.
- Alert on SYN queue saturation, connection table exhaustion, and elevated TCP half-open connections.
- Detect anomalous geographic traffic patterns or sudden increases from specific ASN ranges.
- Track HTTP error rate spikes (502/503/504) and response latency degradation during attacks.
- Identify amplification attack signatures in DNS, NTP, and SSDP traffic logs.

## Mitigation & Best Practices

- **Anycast BGP Routing**: Distribute incoming traffic across a globally distributed network of edge nodes to absorb volumetric floods.
- **SYN Cookies**: Protect against TCP SYN floods by encoding connection parameters without allocating kernel memory.
- **Rate Limiting & CAPTCHA**: Deploy WAF rules to rate-limit aggressive IP ranges and challenge suspicious HTTP floods.
- **DDoS Scrubbing Services**: Route traffic through cloud-based scrubbing centers (Cloudflare, Akamai, AWS Shield) during attacks.
- **Capacity Planning**: Maintain excess bandwidth capacity (2-3x normal peak) to absorb smaller attacks before scrubbing activates.

## Incident Response Considerations

- Activate DDoS response playbook and notify upstream ISP or scrubbing provider immediately.
- Implement geo-blocking or IP blacklisting for confirmed attack sources during active mitigation.
- Preserve traffic captures and flow data for post-incident analysis and potential legal action.
- Communicate service status to stakeholders and customers during extended outages.
- Review and update DDoS playbooks based on attack characteristics observed.

## Framework References

- NIST SP 800-61 (Computer Security Incident Handling Guide)
- CIS Control 12: Network Infrastructure Management
- OWASP Denial of Service Cheat Sheet
