# Artificial Intelligence & LLM Security

## 1. Overview of AI & Machine Learning Security

As Artificial Intelligence (AI) and Large Language Models (LLMs) are integrated into enterprise applications, they introduce novel attack vectors including **Prompt Injection**, **Training Data Poisoning**, and **Model Hallucination Exploitation**.

---

## 2. OWASP Top 10 for LLM Applications

1. **LLM01: Prompt Injection**: Manipulating LLM behavior via crafted inputs to bypass system prompts, execute unintended tools, or exfiltrate context.
   - *Direct Prompt Injection (Jailbreaking)*: User explicitly commands the model to ignore prior instructions.
   - *Indirect Prompt Injection*: Malicious instructions embedded within external data sources (e.g., ingested webpage, PDF, or email).
2. **LLM02: Sensitive Information Disclosure**: Unintentional disclosure of confidential training data, API keys, or system prompts in model responses.
3. **LLM03: Supply Chain Vulnerabilities**: Compromised third-party datasets, pre-trained model weights (PyTorch/TensorFlow models), or vulnerable libraries.
4. **LLM04: Data and Model Poisoning**: Manipulating training datasets or fine-tuning data to introduce backdoors or bias.
5. **LLM05: Improper Output Handling**: Trusting LLM output without sanitization, leading to downstream XSS, SQLi, or Remote Code Execution (RCE).
6. **LLM06: Excessive Agency**: Granting LLMs excessive privileges or tool-access permissions without human-in-the-loop review.
7. **LLM07: System Prompt Leakage**: Extracting proprietary instructions and operational constraints configured in the system prompt.
8. **LLM08: Vector and Embedding Weaknesses**: Exploiting RAG vector stores via adversarial document insertion or similarity manipulation.
9. **LLM09: Misinformation & Hallucination**: Relying on unverified LLM output for critical decisions without automated validation.
10. **LLM10: Unbounded Consumption**: Denial of Service (DoS) attacks targeted at LLM token consumption and API resource limits.

---

## 3. Defense & Security Best Practices

- **Strict Input & Output Sanitization**: Validate all inputs using regex schemas and escape outputs before rendering in HTML/SQL.
- **Principle of Least Privilege for Tool Use**: Limit AI agent execution scopes, enforce strict API permissions, and require human approval for high-risk actions.
- **RAG Integrity Controls**: Hash and sign all document sources before vector indexing; enforce access controls at the vector store layer.
- **Guardrail Integration**: Deploy input/output guardrails (e.g., NeMo Guardrails, Llama Guard) to filter harmful content and prompt injection attempts.
