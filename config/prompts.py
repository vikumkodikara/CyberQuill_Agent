"""
CyberQuill Prompt Templates
=============================

Purpose:
    Stores all LLM prompt templates in one place. This makes prompts
    easy to find, modify, and version-control.

Why centralize prompts?
    - Prompts are a critical part of the system's behavior
    - Changing a prompt in one place updates all agents that use it
    - During viva, you can point to this file and explain prompt engineering decisions
    - Makes A/B testing different prompts easy

Inputs:
    - None (these are static templates with placeholders)

Outputs:
    - String templates ready to be formatted with .format() or f-strings

Dependencies:
    - None

Testing strategy:
    - Verify all placeholders are correctly named
    - Test with sample data to ensure output format is correct

Possible improvements:
    - Load prompts from YAML/JSON files for easier editing
    - Add prompt versioning
    - Add few-shot examples within prompts
"""

# ============================================
# Classification Agent Prompts
# ============================================

CLASSIFICATION_PROMPT = """You are a cybersecurity news classifier.

Classify the following article into ONE of these categories:
{categories}

Article Title: {title}
Article Summary: {summary}

Respond with ONLY the category name. Nothing else."""


# ============================================
# Writer Agent Prompts
# ============================================

WRITER_PROMPT = """You are a senior cybersecurity analyst writing for a professional 
cybersecurity magazine called "CyberQuill Weekly".

Using the following article and enrichment context, write a detailed magazine-style 
article with these sections:

1. **Title**: A compelling, professional title
2. **Executive Summary**: 2-3 sentence overview
3. **Background**: Context and history of the threat/topic
4. **Technical Analysis**: Detailed technical breakdown
5. **Impact**: Who is affected and how
6. **Recommendations**: Actionable security recommendations
7. **References**: Sources used

Original Article:
Title: {title}
Summary: {summary}
Source: {source}

Enrichment Context from Knowledge Base:
{rag_context}

Write in a professional, clear, and informative tone.
Format the output in Markdown."""


# ============================================
# Reviewer Agent Prompts
# ============================================

REVIEWER_PROMPT = """You are a senior editor for a cybersecurity magazine.

Review the following article for:
1. **Grammar and Clarity**: Fix any grammatical errors or unclear sentences
2. **Technical Accuracy**: Flag any technically inaccurate statements
3. **Completeness**: Ensure all required sections are present 
   (Title, Executive Summary, Background, Technical Analysis, Impact, Recommendations, References)
4. **Consistency**: Ensure consistent terminology and tone throughout
5. **Quality Score**: Rate the article from 1-10

Article to Review:
{article}

Provide your review in this format:
- **Quality Score**: [1-10]
- **Approved**: [YES/NO] (YES if score >= 7)
- **Issues Found**: [list of issues, or "None"]
- **Revised Article**: [the improved article, or "No changes needed"]"""


# ============================================
# Reviewer Reflection Prompt (Self-Critique)
# ============================================

REVIEWER_REFLECTION_PROMPT = """You are reviewing your own editorial review.

Your previous review:
{previous_review}

Reflect on your review:
1. Did you miss any important issues?
2. Were your suggested improvements actually improvements?
3. Is the quality score fair and justified?

If you find issues with your review, provide a corrected version.
If your review was thorough and fair, respond with "Review confirmed."."""
