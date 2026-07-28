---
title: SQL Injection Attack Vectors and Prevention
categories: [Vulnerability Management, Data Breach]
keywords: [SQL injection, SQLi, prepared statements, parameterized queries, OWASP, injection]
frameworks: [OWASP Top 10 A03, CWE-89, ASVS]
---

# SQL Injection Attack Vectors and Prevention

## Overview

SQL injection (SQLi) is a code injection technique that exploits vulnerabilities in an application's database layer. It occurs when user-supplied input is incorporated into SQL queries without proper validation or sanitization. SQL injection remains one of the most critical web application vulnerabilities, ranked as A03:2021 – Injection in the OWASP Top 10. Successful attacks can lead to unauthorized data access, authentication bypass, and remote code execution.

## Key Concepts & Attack Vectors

- **Error-Based SQLi**: Crafting input that causes database error messages revealing schema information.
- **Union-Based SQLi**: Using UNION operator to combine injected query results with legitimate results.
- **Boolean-Based Blind SQLi**: Inferring data by observing TRUE/FALSE response differences.
- **Time-Based Blind SQLi**: Using SLEEP() or WAITFOR DELAY commands to extract data via response timing.
- **Second-Order SQLi**: Stored input later incorporated into queries without sanitization at execution time.
- **Authentication Bypass**: Classic `' OR '1'='1` injection to bypass login forms.

## Detection & Indicators

- Web application firewall alerts for SQL metacharacters in request parameters.
- Database error messages containing SQL syntax details in application responses.
- SAST tools detecting string concatenation in SQL query construction.
- DAST tools (SQLMap, Burp Suite, OWASP ZAP) identifying injectable parameters.
- Unusual database query patterns or abnormally long query execution times in database logs.

## Mitigation & Best Practices

- **Parameterized Queries**: Use prepared statements with bound parameters — the most effective defense.
- **Stored Procedures**: Encapsulate database logic with parameterized inputs (avoid dynamic SQL inside).
- **Input Validation**: Apply whitelist validation for data types, length, and format as defense-in-depth.
- **Least Privilege**: Configure database accounts with minimal permissions; never use DBA accounts from web apps.
- **WAF Rules**: Deploy SQL injection detection rules as an additional layer (not sole defense).

## Incident Response Considerations

- Identify all injectable parameters and assess data accessed through exploitation.
- Review database audit logs for unauthorized queries and data exfiltration patterns.
- Patch vulnerable code with parameterized queries and deploy emergency WAF rules.
- Reset credentials for accounts potentially accessed through authentication bypass.
- Conduct full code review for similar injection patterns across the application.

## Framework References

- OWASP Top 10 A03:2021 – Injection
- CWE-89: Improper Neutralization of Special Elements in SQL Command
- OWASP SQL Injection Prevention Cheat Sheet
- OWASP Application Security Verification Standard (ASVS)
