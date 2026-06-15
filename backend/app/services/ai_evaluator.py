import os
import json
import re
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

# Heuristic Rule-Based Fallback
def rule_based_fallback_evaluation(category: str, question: str, answer: str) -> dict:
    answer_lower = answer.lower()
    score = 3
    level = "Defined"
    gaps = []
    strengths = []
    recommendation = ""

    if any(k in answer_lower for k in ["adhoc", "ad-hoc", "manual", "no process", "none", "started"]):
        score = 1
        level = "Initial"
        gaps = ["Lack of standardized processes", "Highly dependent on individual effort"]
        strengths = ["Awareness of the process domain"]
        recommendation = "Establish basic standard operating procedures for this category."
    elif any(k in answer_lower for k in ["some", "developing", "basic", "inconsistent"]):
        score = 2
        level = "Developing"
        gaps = ["Inconsistent execution across projects", "Limited metrics tracking"]
        strengths = ["Partially documented processes"]
        recommendation = "Standardize process templates and checklists to build consistency."
    elif any(k in answer_lower for k in ["automated", "managed", "metrics", "kpi"]):
        score = 4
        level = "Managed"
        gaps = ["Feedback loops not fully closed", "Automation gaps in tool chains"]
        strengths = ["Quantitative process measurements", "Tool-supported workflow enforcement"]
        recommendation = "Integrate tools to compile real-time execution statistics."
    elif any(k in answer_lower for k in ["optimizing", "continuous", "adaptive", "best practice"]):
        score = 5
        level = "Optimizing"
        gaps = ["Minor alignment opportunities with new technology shifts"]
        strengths = ["Root cause analysis routines", "Continuous process optimization focus"]
        recommendation = "Incorporate AI-based automation insights to refine processes continuously."
    else:
        # Default Defined (3)
        gaps = ["Process adherence is undocumented", "Limited integration across tool suites"]
        strengths = ["Defined standard workflows exist"]
        recommendation = "Develop periodic audits to ensure adherence to defined workflows."

    return {
        "score": score,
        "level": level,
        "gaps": gaps,
        "strengths": strengths,
        "recommendation": recommendation
    }

def evaluate_response(category: str, question: str, answer: str) -> dict:
    if not answer or not answer.strip():
        return {
            "score": 1,
            "level": "Initial",
            "gaps": ["No answer provided"],
            "strengths": [],
            "recommendation": "Please answer this question to assess maturity."
        }

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        # Graceful fallback if no API key is configured
        return rule_based_fallback_evaluation(category, question, answer)

    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.2,
            openai_api_key=api_key,
            max_retries=2
        )
        
        template = """You are an enterprise project management maturity expert.
Category: {category}
Question: {question}
User Answer: {answer}

Evaluate this answer and respond ONLY with a valid JSON object matching this schema:
{{
  "score": <integer 1-5>,
  "level": "<Initial|Developing|Defined|Managed|Optimizing>",
  "gaps": ["gap1", "gap2"],
  "strengths": ["strength1"],
  "recommendation": "<one actionable improvement>"
}}
"""
        prompt = PromptTemplate(
            input_variables=["category", "question", "answer"],
            template=template
        )
        
        chain = prompt | llm
        result = chain.invoke({
            "category": category,
            "question": question,
            "answer": answer
        })
        
        # Parse output safely
        text = result.content.strip()
        # Clean markdown code fences (handles ```json, ```JSON, ```, etc.)
        text = re.sub(r'^```(?:json|JSON)?\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'\s*```$', '', text, flags=re.MULTILINE)
        text = text.strip()
        
        return json.loads(text)
    except Exception as e:
        # If API errors, fall back to rule-based analysis
        print(f"AI evaluation failed, using rule-based fallback: {e}")
        return rule_based_fallback_evaluation(category, question, answer)
