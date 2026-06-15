"""Resource Agent — analyzes team allocation, spots overloading, and recommends rebalancing."""
import re
from app.agents import BaseAgent

RESOURCE_PROMPT = """You are an expert resource management analyst specializing in enterprise project portfolios.
Analyze the project portfolio data and answer resource-related questions.

Structure your response with:
1. **Resource Overview** — Total headcount, allocation patterns
2. **Overallocation Risks** — Team members or projects that appear overloaded
3. **Capacity Gaps** — Skills or roles that are under-resourced
4. **Recommendations** — Concrete rebalancing or hiring suggestions

Always reference actual team member names and project data. Be specific and actionable."""


class ResourceAgent(BaseAgent):
    def __init__(self):
        super().__init__(RESOURCE_PROMPT, "ResourceAgent")

    def _run_fallback(self, context: str, question: str) -> dict:
        """Rule-based resource analysis fallback."""
        lines = context.split("\n")
        
        # Extract team sizes and resource info
        total_team = 0
        projects_info = []
        current_project = None
        
        for line in lines:
            project_match = re.search(r"PROJECT:\s*(.+)", line)
            if project_match:
                current_project = project_match.group(1).strip()
            
            team_match = re.search(r"Team Size:\s*(\d+)", line)
            if team_match and current_project:
                size = int(team_match.group(1))
                total_team += size
                projects_info.append((current_project, size))

        # Detect what the user is asking about
        question_lower = question.lower()
        include_overview = True
        include_risks = True
        include_gaps = True
        include_recommendations = True
        
        # Filter response sections based on question keywords
        if "allocation" in question_lower or "utilization" in question_lower:
            include_risks = False
            include_gaps = False
        elif "understaffed" in question_lower or "under-resourced" in question_lower:
            include_risks = False
        elif "risks" in question_lower or "overload" in question_lower:
            include_gaps = False
            include_recommendations = False

        response_parts = []
        
        if include_overview:
            response_parts.append("## Resource Overview\n")
            response_parts.append(f"Total portfolio headcount: **{total_team} team members** across {len(projects_info)} projects.\n\n")

            if projects_info:
                response_parts.append("| Project | Team Size |\n|---|---|\n")
                for name, size in projects_info:
                    flag = " ⚠️" if size <= 3 else ""
                    response_parts.append(f"| {name} | {size}{flag} |\n")

        if include_risks:
            response_parts.append("\n## Overallocation Risks\n")
            small_teams = [(n, s) for n, s in projects_info if s <= 3]
            if small_teams:
                for name, size in small_teams:
                    response_parts.append(f"- **{name}** has only {size} members — high bus factor risk\n")
            else:
                response_parts.append("- No critical overallocation detected\n")

        if include_gaps:
            response_parts.append("\n## Capacity Gaps\n")
            response_parts.append("- Review skill-to-project alignment to identify gaps\n")

        if include_recommendations:
            response_parts.append("\n## Recommendations\n")
            response_parts.append("- Cross-train team members to reduce single-point-of-failure risks\n")
            response_parts.append("- Consider shared resource pools across projects with complementary timelines\n")
            response_parts.append("- Monitor utilization rates weekly to detect burnout signals early\n")

        return {"agent": self.agent_name, "response": "\n".join(response_parts)}
