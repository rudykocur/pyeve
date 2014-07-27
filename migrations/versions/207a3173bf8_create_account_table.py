"""create account table

Revision ID: 207a3173bf8
Revises: None
Create Date: 2014-07-26 23:18:02.333820

"""

# revision identifiers, used by Alembic.
revision = '207a3173bf8'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'account',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('email', sa.String(100), nullable=False, unique=True),
    )


def downgrade():
    op.drop_table('account')
