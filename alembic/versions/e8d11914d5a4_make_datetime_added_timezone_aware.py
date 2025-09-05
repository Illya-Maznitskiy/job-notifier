"""make datetime_added timezone aware

Revision ID: e8d11914d5a4
Revises: d4db075e2d04
Create Date: 2025-09-06 00:54:46.068198

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e8d11914d5a4'
down_revision: Union[str, Sequence[str], None] = 'd4db075e2d04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
