"""merge branches

Revision ID: 455e61854f2a
Revises: 2bb3d633479b, a928fa7fc3ab
Create Date: 2026-08-21 09:00:31.877198

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '455e61854f2a'
down_revision = ('2bb3d633479b', 'a928fa7fc3ab')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
