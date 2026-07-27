# IoT & Firmware Security

## 1. Introduction

**Internet of Things (IoT) & Embedded Security** focuses on securing physical connected devices, microcontrollers, and real-time operating systems (RTOS) across smart home, industrial control (ICS/SCADA), and medical device environments.

---

## 2. Common Embedded Attack Vectors

- **Hardcoded Credentials & Backdoors**: Default admin passwords embedded directly into factory firmware binaries.
- **Unencrypted Firmware Updates**: Over-the-Air (OTA) update mechanisms lacking cryptographic signature validation, vulnerable to Man-in-the-Middle (MitM) image tampering.
- **Exposed Physical Debug Interfaces**: Insecure JTAG, SWD, or UART pinouts providing root shell access to physical attackers.
- **Insecure Wireless & IoT Protocols**: Unencrypted MQTT topics, CoAP without DTLS, or vulnerable Bluetooth Low Energy (BLE) pairings.

---

## 3. Firmware Analysis Methodology

1. **Extraction**: Dump firmware from SPI flash chips using physical programmers (Flashrom, Bus Pirate) or extract from vendor update `.bin` packages using `binwalk`.
2. **File System Unpacking**: Extract SquashFS, CramFS, or YAFFS2 file systems to analyze configuration files (`/etc/shadow`, `/etc/passwd`).
3. **Static Binary Inspection**: Search for hardcoded API keys, private RSA keys, or vulnerable C string functions (`strcpy`, `sprintf`) in web server executables.
4. **Remediation**: Sign all OTA updates using asymmetric PKI keys, disable hardware debug ports in production, and enforce secure boot (Root of Trust).
