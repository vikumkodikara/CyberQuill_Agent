# Cryptography & Public Key Infrastructure (PKI)

## 1. Fundamentals

**Cryptography** provides data confidentiality, integrity, authentication, and non-repudiation across digital communications.

---

## 2. Core Cryptographic Algorithms

- **Symmetric Encryption**: Uses a single shared key for encryption and decryption.
  - *AES-256 (Advanced Encryption Standard)*: Industry benchmark for bulk data encryption at rest and in transit.
- **Asymmetric Encryption**: Uses a public key for encryption/verification and a private key for decryption/signing.
  - *RSA & ECC (Elliptic Curve Cryptography)*: ECC offers equivalent security to RSA with significantly smaller key sizes (e.g., 256-bit ECC ≈ 3072-bit RSA).
- **Cryptographic Hash Functions**: One-way algorithms producing fixed-size digests (SHA-256, SHA-3) used for data integrity verification.

---

## 3. Public Key Infrastructure (PKI) Architecture

```
[ Root CA ] ──▶ [ Intermediate CA ] ──▶ [ End-Entity Certificate (TLS/SSL) ]
```

- **Certificate Authority (CA)**: Trusted entity that signs and issues digital certificates (X.509 standard).
- **Certificate Revocation List (CRL) & OCSP**: Protocols for verifying if a certificate has been revoked before expiration.
- **TLS 1.3**: Latest transport layer security standard, enforcing Perfect Forward Secrecy (PFS) via Ephemeral Diffie-Hellman key exchange.

---

## 4. Post-Quantum Cryptography (PQC)

Quantum computers using Shor's algorithm threaten legacy RSA/ECC asymmetric encryption. Organizations are preparing for migration to NIST-standardized Post-Quantum algorithms (e.g., CRYSTALS-Kyber, CRYSTALS-Dilithium).
