# Distributed Denial of Service (DDoS) & Mitigation

## 1. Overview

A **Distributed Denial of Service (DDoS)** attack attempts to exhaust the bandwidth, computing power, or connection pools of a target system by flooding it with traffic originating from a botnet of compromised devices.

---

## 2. Main Attack Vector Classification

- **Volumetric Attacks (Layer 3/4)**: Saturation of internet bandwidth using massive traffic volumes.
  - *UDP Amplification*: Abuse of open NTP, DNS, or Memcached servers to multiply request sizes toward a spoofed target IP.
- **Protocol Attacks (Layer 3/4)**: Consuming infrastructure state table limits (firewalls, load balancers).
  - *SYN Flood*: Sending half-open TCP connection requests until SYN queue capacity is breached.
- **Application Layer Attacks (Layer 7)**: Targeting specific web applications or database queries to exhaust CPU/Memory.
  - *HTTP GET/POST Flood*: Sending complex, resource-intensive requests (e.g., PDF generation or SQL search queries).

---

## 3. Defense & Scrubbing Mechanisms

- **Anycast BGP Routing**: Distributes incoming traffic across a globally distributed network of edge nodes to absorb volumetric floods.
- **SYN Cookies**: Protects against TCP SYN floods by encoding connection parameters into the initial SYN-ACK sequence number without allocating kernel memory.
- **Rate Limiting & CAPTCHA Enforcement**: Deploying WAF rules to rate-limit aggressive IP ranges and challenge suspicious HTTP floods.
