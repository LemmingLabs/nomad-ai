"""merge trips heads

Revision ID: def156246f1c
Revises: 284999202e63, a98adce4c66b
Create Date: 2026-04-18 23:01:27.530819

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'def156246f1c'
down_revision: Union[str, Sequence[str], None] = ('284999202e63', 'a98adce4c66b')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
