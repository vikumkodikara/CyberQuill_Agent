# Container & Kubernetes Security

## 1. Overview

Containerized architectures and orchestrators like Kubernetes (K8s) increase deployment velocity but introduce specialized attack vectors around image vulnerabilities, cluster RBAC misconfigurations, and container breakout risks.

---

## 2. Docker & Container Image Best Practices

- **Minimal Base Images**: Build container images using minimal bases (e.g., `distroless` or `alpine`) to eliminate unnecessary tools like `curl`, `netcat`, or `bash`.
- **Non-Root Containers**: Execute applications under non-root users (`USER 10001`) inside Dockerfiles.
- **Immutable & Read-Only File Systems**: Mount container root file systems as read-only (`--read-only`) to restrict runtime malware persistence.
- **Image Signature Verification**: Verify container image signatures (e.g., Sigstore/Cosign) before deployment.

---

## 3. Kubernetes Cluster Hardening (CIS Benchmarks)

- **Pod Security Standards (PSS)**: Enforce `Restricted` security profiles to block privileged containers (`privileged: true`), host namespace sharing, and root capabilities.
- **Kubernetes RBAC**: Restrict ServiceAccount permissions using granular Role and ClusterRole bindings.
- **Network Policies**: Enforce default-deny ingress and egress policies to prevent unauthorized pod-to-pod communication.
- **Runtime Threat Detection**: Deploy eBPF-based security monitoring (e.g., Falco) to detect unauthorized shell execution or syscall anomalies inside running containers.
