"""Timeline Agent — analyzes sprint velocity, predicts delays, identifies schedule bottlenecks."""
import re
from app.agents import BaseAgent

TIMELINE_PROMPT = """You are an expert project timeline analyst specializing in Agile delivery metrics.
Analyze the project portfolio data and answer timeline-related questions.

Structure your response with:
1. **Timeline Status** — Which projects are on track, behind, or ahead of schedule
2. **Velocity Trends** — Sprint velocity analysis and trajectory predictions
3. **Delay Risk Factors** — What's causing or likely to cause schedule slippage
4. **Schedule Recommendations** — Concrete actions to get back on track

Always reference actual sprint data, dates, and project names. Be specific and data-driven."""


class TimelineAgent(BaseAgent):
    def __init__(self):
        super().__init__(TIMELINE_PROMPT, "TimelineAgent")

    def _run_fallback(self, context: str, question: str) -> dict:
        """Rule-based timeline analysis fallback."""
        lines = context.split("\n")
        
        current_project = None
        projects = {}
        
        for line in lines:
            project_match = re.search(r"PROJECT:\s*(.+)", line)
            if project_match:
                current_project = project_match.group(1).strip()
                projects[current_project] = {"status": "", "trend": "", "sprints": ""}
            
            if current_project:
                if "Status:" in line:
                    status_match = re.search(r"Status:\s*(\S+)", line)
                    if status_match:
                        projects[current_project]["status"] = status_match.group(1)
                
                if "Velocity Trend:" in line:
                    trend_match = re.search(r"Velocity Trend:\s*(\S+)", line)
                    if trend_match:
                        projects[current_project]["trend"] = trend_match.group(1)
                
                if "Sprints:" in line:
                    projects[current_project]["sprints"] = line.strip()

        # Detect what the user is asking about
        question_lower = question.lower()
        include_status = True
        include_trends = True
        include_risks = True
        include_recommendations = True
        
        # Filter response sections based on question keywords
        if "velocity" in question_lower or "trend" in question_lower:
            include_status = False
            include_risks = False
            include_recommendations = False
        elif "delay" in question_lower or "late" in question_lower or "behind" in question_lower:
            include_trends = False
            include_recommendations = False
        elif "on track" in question_lower or "green" in question_lower or "healthy" in question_lower:
            include_risks = False

        response_parts = []
        
        delayed = [n for n, d in projects.items() if d["status"] == "delayed"]
        at_risk = [n for n, d in projects.items() if d["status"] == "at_risk"]
        on_track = [n for n, d in projects.items() if d["status"] == "on_track"]
        
        if include_status:
            response_parts.append("## Timeline Status\n")
            
            if delayed:
                response_parts.append(f"🔴 **Delayed ({len(delayed)}):** {', '.join(delayed)}\n")
            if at_risk:
                response_parts.append(f"🟡 **At Risk ({len(at_risk)}):** {', '.join(at_risk)}\n")
            if on_track:
                response_parts.append(f"🟢 **On Track ({len(on_track)}):** {', '.join(on_track)}\n")

        if include_trends:
            response_parts.append("\n## Velocity Trends\n")
            declining = [n for n, d in projects.items() if d["trend"] == "declining"]
            if declining:
                for name in declining:
                    response_parts.append(f"- **{name}**: Velocity is **declining** — investigate blockers and team capacity\n")
            else:
                response_parts.append("- All active projects show stable or improving velocity trends\n")

        if include_risks:
            response_parts.append("\n## Delay Risk Factors\n")
            if delayed:
                response_parts.append(f"- {delayed[0]} has exceeded its target end date and requires immediate recovery planning\n")
            if include_trends:
                declining = [n for n, d in projects.items() if d["trend"] == "declining"]
                if declining:
                    response_parts.append(f"- Declining velocity in {', '.join(declining)} suggests emerging blockers\n")
            if not delayed and (not include_trends or not [n for n, d in projects.items() if d["trend"] == "declining"]):
                response_parts.append("- No significant delay risks detected in current sprint data\n")

        if include_recommendations:
            response_parts.append("\n## Schedule Recommendations\n")
            response_parts.append("- Conduct sprint retrospective focused on impediment removal\n")
            response_parts.append("- Review scope commitments against actual team capacity\n")
            response_parts.append("- Implement buffer sprints for projects approaching deadlines\n")

        return {"agent": self.agent_name, "response": "\n".join(response_parts)}
