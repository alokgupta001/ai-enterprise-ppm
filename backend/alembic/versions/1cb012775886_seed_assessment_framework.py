"""seed_assessment_framework

Revision ID: 1cb012775886
Revises: c720dbf13907
Create Date: 2026-06-10 15:02:59.450904
"""

from typing import Sequence, Union
from uuid import uuid4

from alembic import op
import sqlalchemy as sa

revision: str = "1cb012775886"
down_revision: Union[str, Sequence[str], None] = "c720dbf13907"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# UUID for the seeded framework - must be deterministic for downgrades
FRAMEWORK_UUID = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"


def upgrade():

    framework_id = FRAMEWORK_UUID

    op.execute(f"""
        INSERT INTO maturity_frameworks
        (id, name, description, version, created_at, updated_at, is_deleted)
        VALUES (
            '{framework_id}',
            'Enterprise Project Management Maturity Model',
            'Enterprise PMO maturity assessment framework',
            '1.0',
            NOW(),
            NOW(),
            FALSE
        )
    """)

    categories = [
        ("Portfolio Governance", 1.2),
        ("Agile Delivery", 1.1),
        ("Resource Management", 1.0),
        ("Risk & Issue Management", 1.3),
        ("PMO Capability", 1.4),
    ]

    category_ids = {}

    for index, (name, weight) in enumerate(categories):

        category_id = str(uuid4())
        category_ids[name] = category_id

        op.execute(f"""
            INSERT INTO assessment_categories
            (
                id,
                framework_id,
                name,
                weight,
                order_index,
                created_at,
                updated_at,
                is_deleted
            )
            VALUES (
                '{category_id}',
                '{framework_id}',
                '{name}',
                {weight},
                {index},
                NOW(),
                NOW(),
                FALSE
            )
        """)

    questions = {
        "Portfolio Governance": [
            "How are project investment decisions approved and governed?",
            "How are project priorities aligned with business objectives?",
            "How are project risks escalated to executive leadership?",
            "How are governance reviews conducted?",
            "How are compliance requirements monitored?"
        ],

        "Agile Delivery": [
            "How consistently are Agile practices followed across teams?",
            "How is sprint performance measured?",
            "How are backlog priorities managed?",
            "How are dependencies handled?",
            "How are retrospective outcomes implemented?"
        ],

        "Resource Management": [
            "How is resource capacity planning performed?",
            "How are skill gaps identified?",
            "How is resource utilization measured?",
            "How are resource conflicts resolved?",
            "How are critical resources allocated?"
        ],

        "Risk & Issue Management": [
            "How are project risks identified?",
            "How are risks prioritized?",
            "How are mitigation plans tracked?",
            "How are recurring issues analyzed?",
            "How are lessons learned incorporated?"
        ],

        "PMO Capability": [
            "How does the PMO measure portfolio performance?",
            "How are benefits realization metrics tracked?",
            "How is executive reporting generated?",
            "How are project standards enforced?",
            "How does the PMO support transformation initiatives?"
        ]
    }

    for category_name, question_list in questions.items():

        category_id = category_ids[category_name]

        for idx, question in enumerate(question_list):

            op.execute(f"""
                INSERT INTO assessment_questions
                (
                    id,
                    category_id,
                    question_text,
                    question_type,
                    max_score,
                    order_index,
                    created_at,
                    updated_at,
                    is_deleted
                )
                VALUES (
                    '{uuid4()}',
                    '{category_id}',
                    '{question}',
                    'text',
                    5,
                    {idx},
                    NOW(),
                    NOW(),
                    FALSE
                )
            """)


def downgrade():
    # Only delete the seeded framework and its associated data
    op.execute(f"DELETE FROM assessment_questions WHERE category_id IN (SELECT id FROM assessment_categories WHERE framework_id = '{FRAMEWORK_UUID}')")
    op.execute(f"DELETE FROM assessment_categories WHERE framework_id = '{FRAMEWORK_UUID}'")
    op.execute(f"DELETE FROM maturity_frameworks WHERE id = '{FRAMEWORK_UUID}'")