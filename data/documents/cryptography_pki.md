---
title: Cryptography & Public Key Infrastructure
categories: [Vulnerability Management, Data Breach]
keywords: [cryptography, PKI, TLS, AES, RSA, ECC, post-quantum, certificates]
frameworks: [NIST FIPS 140-3, NIST PQC, X.509, TLS 1.3]
---

# Cryptography & Public Key Infrastructure (PKI)

## Overview

Cryptography provides data confidentiality, integrity, authentication, and non-repudiation across digital communications. Public Key Infrastructure (PKI) establishes the trust framework for digital certificates, enabling secure TLS connections, code signing, and encrypted data exchange across enterprise systems.

## Key Concepts & Attack Vectors

- **Symmetric Encryption**: AES-256 for bulk data encryption at rest and in transit using a single shared key.
- **Asymmetric Encryption**: RSA and ECC for key exchange and digital signatures; 256-bit ECC provides security equivalent to 3072-bit RSA.
- **Cryptographic Hash Functions**: SHA-256 and SHA-3 for data integrity verification and password storage.
- **Certificate Authority Chain**: Root CA issues intermediate CA certificates, which sign end-entity TLS/SSL certificates.
- **Post-Quantum Threat**: Quantum computers using Shor's algorithm threaten legacy RSA/ECC asymmetric encryption.

## Detection & Indicators

- Scan for deprecated protocols (SSLv3, TLS 1.0/1.1) and weak cipher suites in network traffic.
- Detect expired, self-signed, or improperly chained certificates in TLS handshakes.
- Monitor for certificate transparency log entries indicating unauthorized certificate issuance.
- Alert on use of MD5, SHA-1, or DES/3DES algorithms in production systems.
- Identify private key exposure in code repositories, configuration files, or memory dumps.

## Mitigation & Best Practices

- **TLS 1.3 Enforcement**: Mandate TLS 1.3 with Perfect Forward Secrecy via ephemeral Diffie-Hellman key exchange.
- **Certificate Lifecycle Management**: Automate certificate provisioning, renewal, and revocation via ACME or enterprise PKI.
- **Key Management**: Store private keys in HSMs or cloud KMS; never embed keys in source code.
- **OCSP Stapling**: Enable OCSP stapling to verify certificate revocation status without performance penalty.
- **Post-Quantum Migration**: Begin inventory and migration planning for NIST-standardized PQC algorithms (CRYSTALS-Kyber, CRYSTALS-Dilithium).

## Incident Response Considerations

- Revoke compromised certificates immediately via CRL and OCSP updates.
- Rotate all keys and certificates if private key material is exposed.
- Assess scope of data intercepted if weak encryption was used during the compromise window.
- Re-issue certificates from a clean CA chain after root or intermediate CA compromise.
- Document cryptographic failures for regulatory breach notification requirements.

## Framework References

- NIST FIPS 140-3 (Cryptographic Module Validation)
- NIST Post-Quantum Cryptography Standards
- X.509 Certificate Standard (RFC 5280)
- TLS 1.3 Specification (RFC 8446)
