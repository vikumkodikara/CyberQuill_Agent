---
title: Container & Kubernetes Security
categories: [Cloud Security, Vulnerability Management]
keywords: [Docker, Kubernetes, container, K8s, RBAC, pod security, image scanning]
frameworks: [CIS Kubernetes Benchmark, NIST SP 800-190, OWASP Kubernetes Top 10]
---

# Container & Kubernetes Security

## Overview

Container and Kubernetes security addresses risks in containerized application deployments across Docker and orchestration platforms. Misconfigured clusters, vulnerable container images, and excessive permissions are leading causes of cloud-native breaches. Security must be embedded across the container lifecycle from image build through runtime.

## Key Concepts & Attack Vectors

- **Vulnerable Container Images**: Base images with unpatched CVEs deployed to production clusters.
- **Privileged Container Escape**: Containers running as root with host namespace access enabling node compromise.
- **Kubernetes RBAC Misconfiguration**: Overly permissive service accounts and cluster roles granting excessive access.
- **Secrets in Environment Variables**: API keys and credentials exposed in container configurations and logs.
- **Unrestricted Network Policies**: Pods communicating freely without network segmentation within clusters.

## Detection & Indicators

- Container runtime alerts for suspicious process execution (shell spawning, crypto mining).
- Image scanning results flagging critical CVEs in deployed container images.
- Audit logs showing unauthorized kubectl commands or API server access.
- Detection of privileged pod creation or hostPath volume mounts in namespaces.
- Network flow analysis revealing unexpected pod-to-pod communication patterns.

## Mitigation & Best Practices

- **Image Scanning**: Scan all container images in CI/CD and registry before deployment (Trivy, Grype).
- **Pod Security Standards**: Enforce restricted pod security policies prohibiting privileged containers.
- **RBAC Least Privilege**: Grant minimal Kubernetes permissions per service account and namespace.
- **Network Policies**: Implement default-deny network policies with explicit allow rules between pods.
- **Secrets Management**: Use Kubernetes Secrets with encryption at rest or external vault integration.

## Incident Response Considerations

- Isolate compromised pods and namespaces using network policies and admission controllers.
- Preserve container logs and runtime forensics before terminating affected workloads.
- Rotate all secrets mounted in compromised containers and namespaces.
- Audit cluster RBAC for privilege escalation paths used during the attack.
- Rebuild affected container images from patched base images after eradication.

## Framework References

- CIS Kubernetes Benchmark v1.8
- NIST SP 800-190 (Application Container Security Guide)
- OWASP Kubernetes Top 10
- NSA/CISA Kubernetes Hardening Guidance
