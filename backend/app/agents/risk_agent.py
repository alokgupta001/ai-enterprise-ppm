"""Risk Agent — analyzes project risks, severity, and recommends mitigations."""
import re
from app.agents import BaseAgent

RISK_PROMPT = """You are an expert project risk analyst with 15 years of enterprise PMO experience.
Analyze the project portfolio data and answer risk-related questions.

Structure your response with:
1. **Risk Assessment Summary** — Overall risk posture of the portfolio
2. **Critical Risks** — Top 3 risks that need immediate attention, referencing specific projects
3. **Recommended Mitigations** — Concrete, actionable steps
4. **Risk Score** — Overall portfolio risk rating (1-10, where 10 is highest risk)

Always reference actual project names and data from the context. Be specific and actionable."""


class RiskAgent(BaseAgent):
    def __init__(self):
        super().__init__(RISK_PROMPT, "RiskAgent")

    def _run_fallback(self, context: str, question: str) -> dict:
        """Rule-based risk analysis fallback."""
        lines = context.split("\n")
        high_risks = []
        at_risk_projects = []
        delayed_projects = []
        
        # Maintain state across iterations
        current_project_name = None

        for line in lines:
            # First, extract and track project name
            if "PROJECT:" in line:
                match = re.search(r"PROJECT:\s*(.+)", line)
                if match:
                    current_project_name = match.group(1).strip()
            
            # Then check for status indicators on this or subsequent lines
            if "[HIGH]" in line:
                high_risks.append(line.strip())
            if "at_risk" in line.lower() and current_project_name:
                at_risk_projects.append(current_project_name)
            if "delayed" in line.lower() and current_project_name:
                delayed_projects.append(current_project_name)

        # Detect what the user is asking about
        question_lower = question.lower()
        include_summary = True
        include_critical = True
        include_mitigations = True
        
        # If user asks only about specific aspects, filter the response
        if "score" in question_lower or "rating" in question_lower:
            include_critical = False
            include_mitigations = False

        response_parts = []
        
        if include_summary:
            response_parts.append("## Risk Assessment Summary\n")
            
            if delayed_projects or at_risk_projects:
                response_parts.append(
                    f"The portfolio has **{len(at_risk_projects)} at-risk** and "
                    f"**{len(delayed_projects)} delayed** project(s) requiring immediate attention.\n"
                )
            else:
                response_parts.append("The portfolio is in a healthy state with no critical delays.\n")

        if include_critical:
            if high_risks:
                response_parts.append("## Critical Risks\n")
                for i, risk in enumerate(high_risks[:3], 1):
                    response_parts.append(f"{i}. {risk}\n")

        if include_mitigations:
            response_parts.append("\n## Recommended Mitigations\n")
            response_parts.append("- Escalate high-severity risks to executive steering committee\n")
            response_parts.append("- Implement weekly risk review cadence for at-risk projects\n")
            response_parts.append("- Create contingency resource pools for critical path activities\n")

        risk_score = min(10, len(high_risks) * 2 + len(delayed_projects) * 3 + len(at_risk_projects))
        response_parts.append(f"\n**Portfolio Risk Score: {risk_score}/10**")

        return {"agent": self.agent_name, "response": "\n".join(response_parts)}
