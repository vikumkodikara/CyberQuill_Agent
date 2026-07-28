---
title: Artificial Intelligence & LLM Security
categories: [AI Security, Vulnerability Management]
keywords: [prompt injection, LLM, AI security, model poisoning, RAG, embeddings]
frameworks: [OWASP LLM Top 10, NIST AI RMF]
---

# Artificial Intelligence & LLM Security

## Overview

As Artificial Intelligence (AI) and Large Language Models (LLMs) are integrated into enterprise applications, they introduce novel attack vectors including prompt injection, training data poisoning, and model hallucination exploitation. Organizations deploying AI systems must treat LLM pipelines as untrusted input surfaces requiring defense-in-depth controls comparable to web application security.

## Key Concepts & Attack Vectors

1. **LLM01: Prompt Injection** — Manipulating LLM behavior via crafted inputs to bypass system prompts, execute unintended tools, or exfiltrate context. Direct injection (jailbreaking) and indirect injection (malicious content in ingested documents) are both critical threats.
2. **LLM02: Sensitive Information Disclosure** — Unintentional disclosure of confidential training data, API keys, or system prompts in model responses.
3. **LLM04: Data and Model Poisoning** — Manipulating training or fine-tuning datasets to introduce backdoors or bias.
4. **LLM05: Improper Output Handling** — Trusting LLM output without sanitization, leading to downstream XSS, SQL injection, or remote code execution.
5. **LLM08: Vector and Embedding Weaknesses** — Exploiting RAG vector stores via adversarial document insertion or similarity manipulation.

## Detection & Indicators

- Monitor for anomalous token consumption spikes indicating prompt flooding or unbounded consumption attacks.
- Log and alert on system prompt leakage attempts and repeated jailbreak patterns in user inputs.
- Detect unauthorized tool invocations or privilege escalations from AI agents with excessive agency.
- Scan ingested RAG documents for hidden prompt injection payloads embedded in white text or metadata.
- Track model output drift and hallucination rates against baseline quality metrics.

## Mitigation & Best Practices

- **Strict Input & Output Sanitization**: Validate all inputs using schema validation and escape outputs before rendering in HTML or SQL contexts.
- **Principle of Least Privilege for Tool Use**: Limit AI agent execution scopes, enforce strict API permissions, and require human approval for high-risk actions.
- **RAG Integrity Controls**: Hash and sign all document sources before vector indexing; enforce access controls at the vector store layer.
- **Guardrail Integration**: Deploy input/output guardrails (e.g., NeMo Guardrails, Llama Guard) to filter harmful content and prompt injection attempts.
- **Supply Chain Security**: Verify integrity of pre-trained model weights and third-party datasets before deployment.

## Incident Response Considerations

- Isolate compromised AI pipelines and revoke API keys immediately upon detecting prompt injection or data exfiltration.
- Preserve prompt logs and model interaction traces for forensic analysis.
- Roll back to known-good model versions and re-index RAG knowledge bases after poisoning incidents.
- Notify affected users if sensitive data was disclosed through model responses.
- Conduct post-incident review of system prompt design and tool permission boundaries.

## Framework References

- OWASP Top 10 for LLM Applications (LLM01–LLM10)
- NIST AI Risk Management Framework (AI RMF 1.0)
- MITRE ATLAS (Adversarial Threat Landscape for AI Systems)
