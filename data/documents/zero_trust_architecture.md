# Zero Trust Architecture (ZTA)

## 1. Core Philosophy

**Zero Trust** is a strategic cybersecurity paradigm operating on the fundamental mandate: **"Never Trust, Always Verify."** Unlike traditional perimeter-based security ("castle-and-moat"), Zero Trust assumes that threats exist both outside and inside the network boundary.

---

## 2. Fundamental Pillars of Zero Trust (NIST SP 800-207)

1. **Continuous Identity Verification**: Authenticate and authorize every access request dynamically using Multi-Factor Authentication (MFA) and risk-based context.
2. **Explicit Authorization**: Evaluate device health, user context, geographical location, and resource sensitivity before granting access.
3. **Least Privilege Access (JIT/JEA)**: Provide Just-In-Time (JIT) and Just-Enough-Access (JEA) to minimize the attack surface.
4. **Micro-segmentation**: Divide networks into isolated security zones to restrict lateral movement during a breach.
5. **Assume Breach**: Operate with the mindset that attackers are already present in the environment; encrypt all internal traffic (mTLS) and log all activity.

---

## 3. Key Components of ZTA Implementation

- **Policy Engine (PE)**: Evaluates access requests against enterprise security policies.
- **Policy Administrator (PA)**: Communicates with the Policy Enforcement Point (PEP) to issue session tokens or access credentials.
- **Policy Enforcement Point (PEP)**: Intercepts, inspects, and terminates connections between users and enterprise resources.
- **Software-Defined Perimeter (SDP)**: Hides infrastructure assets from public view, rendering services invisible until authenticated.

---

## 4. Operational Benefits

- Eliminates implicit trust based on network location (LAN vs. Internet).
- Drastically limits blast radius during ransomware outbreaks or credential theft.
- Enables secure remote workforce access without legacy VPN vulnerabilities.
