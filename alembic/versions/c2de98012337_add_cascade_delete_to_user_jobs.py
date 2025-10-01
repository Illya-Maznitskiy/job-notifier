"""add cascade delete to user_jobs

Revision ID: c2de98012337
Revises: de496a1454d0
Create Date: 2025-10-01 17:40:40.488223

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c2de98012337"
down_revision: Union[str, Sequence[str], None] = "de496a1454d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(
        "user_jobs_job_id_fkey", "user_jobs", type_="foreignkey"
    )
    op.create_foreign_key(
        None, "user_jobs", "jobs", ["job_id"], ["id"], ondelete="CASCADE"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(None, "user_jobs", type_="foreignkey")
    op.create_foreign_key(
        "user_jobs_job_id_fkey", "user_jobs", "jobs", ["job_id"], ["id"]
    )
