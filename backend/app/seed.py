"""
Seed script for populating realistic project data for Module 2.
Run: python -m app.seed  (from backend/ directory with venv active)
"""
from datetime import date, timedelta
from app.database import SessionLocal
from app.models.project import Project, ProjectRisk, ProjectResource, SprintData
from app.models.organization import Organization
from app.models.user import User
from app.models.enums import UserRole
from app.core.security import hash_password


def seed_projects():
    db = SessionLocal()
    try:
        # Find first org, or create a default one
        org = db.query(Organization).filter(Organization.is_deleted.is_(False)).first()
        if not org:
            print("No organization found. Creating default organization 'Acme Corp'...")
            org = Organization(
                name="Acme Corp",
                industry="Technology",
                employee_count=500
            )
            db.add(org)
            db.flush()
            
            # Create default admin user
            print("Creating default admin user 'admin@acme.com' with password 'password123'...")
            admin = User(
                name="Admin User",
                email="admin@acme.com",
                password_hash=hash_password("password123"),
                role=UserRole.ADMIN,
                organization_id=org.id
            )
            db.add(admin)
            db.commit()

        org_id = org.id

        # Check if projects already seeded
        existing = db.query(Project).filter(Project.org_id == org_id).count()
        if existing > 0:
            print(f"Projects already seeded ({existing} found). Skipping.")
            return

    today = date.today()

    projects_data = [
        {
            "name": "ERP Modernization",
            "status": "at_risk",
            "health_score": 62,
            "budget": 500000,
            "budget_used": 340000,
            "start_date": today - timedelta(days=120),
            "target_end_date": today + timedelta(days=60),
            "team_size": 12,
            "risks": [
                ("Legacy system integration failures causing data migration delays", "high"),
                ("Key architect on medical leave for 3 weeks", "high"),
                ("Vendor API deprecation announced for Q3", "medium"),
            ],
            "resources": [
                ("Sarah Chen", 100, "Tech Lead", "Java, Spring Boot, Oracle"),
                ("Raj Patel", 80, "Backend Dev", "Python, SQL, ETL"),
                ("Emily Wong", 100, "PM", "Agile, Stakeholder Mgmt"),
                ("Alex Kim", 60, "QA Lead", "Selenium, Performance Testing"),
            ],
            "sprints": [
                (1, 28, 85.0), (2, 32, 78.0), (3, 24, 65.0),
                (4, 18, 52.0), (5, 22, 60.0),
            ],
        },
        {
            "name": "Mobile App Launch",
            "status": "on_track",
            "health_score": 88,
            "budget": 150000,
            "budget_used": 95000,
            "start_date": today - timedelta(days=90),
            "target_end_date": today + timedelta(days=30),
            "team_size": 6,
            "risks": [
                ("App Store review process may delay launch by 1 week", "low"),
                ("Push notification service rate limits under load", "medium"),
            ],
            "resources": [
                ("David Park", 100, "Mobile Lead", "React Native, iOS, Android"),
                ("Lisa Kumar", 100, "UI/UX Designer", "Figma, Design Systems"),
                ("Tom Harris", 80, "Backend Dev", "Node.js, Firebase"),
            ],
            "sprints": [
                (1, 30, 92.0), (2, 34, 88.0), (3, 36, 94.0),
                (4, 32, 90.0), (5, 38, 95.0),
            ],
        },
        {
            "name": "Data Migration Platform",
            "status": "delayed",
            "health_score": 41,
            "budget": 200000,
            "budget_used": 190000,
            "start_date": today - timedelta(days=180),
            "target_end_date": today - timedelta(days=15),
            "team_size": 4,
            "risks": [
                ("Budget overrun — 95% consumed with 30% work remaining", "high"),
                ("Source data quality issues causing validation failures", "high"),
                ("Single point of failure — only 1 DBA on team", "high"),
                ("Regulatory compliance deadline in 45 days", "medium"),
            ],
            "resources": [
                ("Mike Johnson", 100, "DBA", "PostgreSQL, ETL, Data Modeling"),
                ("Nina Shah", 60, "Data Analyst", "Python, Pandas, SQL"),
            ],
            "sprints": [
                (1, 20, 70.0), (2, 15, 55.0), (3, 12, 42.0),
                (4, 10, 38.0), (5, 8, 30.0),
            ],
        },
        {
            "name": "Cloud Infrastructure Migration",
            "status": "on_track",
            "health_score": 79,
            "budget": 350000,
            "budget_used": 180000,
            "start_date": today - timedelta(days=60),
            "target_end_date": today + timedelta(days=120),
            "team_size": 8,
            "risks": [
                ("Network latency between on-prem and cloud during cutover", "medium"),
                ("Security compliance audit pending for new cloud env", "medium"),
            ],
            "resources": [
                ("Chris Taylor", 100, "Cloud Architect", "AWS, Terraform, Kubernetes"),
                ("Amy Zhang", 80, "DevOps", "CI/CD, Docker, Ansible"),
                ("James Lee", 100, "SRE", "Monitoring, Incident Response"),
            ],
            "sprints": [
                (1, 25, 80.0), (2, 30, 85.0), (3, 28, 82.0),
                (4, 32, 88.0),
            ],
        },
        {
            "name": "Customer Portal Redesign",
            "status": "completed",
            "health_score": 95,
            "budget": 120000,
            "budget_used": 108000,
            "start_date": today - timedelta(days=200),
            "target_end_date": today - timedelta(days=30),
            "team_size": 5,
            "risks": [
                ("Minor accessibility compliance gaps identified in audit", "low"),
            ],
            "resources": [
                ("Rachel Adams", 100, "Frontend Lead", "React, TypeScript, A11y"),
                ("Ben Cooper", 80, "Backend Dev", "FastAPI, PostgreSQL"),
                ("Sofia Martinez", 100, "UX Researcher", "User Testing, Analytics"),
            ],
            "sprints": [
                (1, 28, 90.0), (2, 32, 92.0), (3, 35, 95.0),
                (4, 36, 96.0), (5, 34, 94.0), (6, 38, 98.0),
            ],
        },
    ]

    for pdata in projects_data:
        project = Project(
            org_id=org_id,
            name=pdata["name"],
            status=pdata["status"],
            health_score=pdata["health_score"],
            budget=pdata["budget"],
            budget_used=pdata["budget_used"],
            start_date=pdata["start_date"],
            target_end_date=pdata["target_end_date"],
            team_size=pdata["team_size"],
        )
        db.add(project)
        db.flush()

        for desc, severity in pdata["risks"]:
            db.add(ProjectRisk(
                project_id=project.id,
                description=desc,
                severity=severity,
            ))

        for name, alloc, role, skills in pdata["resources"]:
            db.add(ProjectResource(
                project_id=project.id,
                resource_name=name,
                allocation_percent=alloc,
                role=role,
                skills=skills,
            ))

        for sprint_num, velocity, completion in pdata["sprints"]:
            db.add(SprintData(
                project_id=project.id,
                sprint_number=sprint_num,
                velocity=velocity,
                completion_rate=completion,
            ))

    db.commit()
    print(f"Seeded {len(projects_data)} projects with risks, resources, and sprint data.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_projects()
