"""Added tables for user and corporation signatures

Revision ID: 1a88eba5f47
Revises: 207a3173bf8
Create Date: 2014-09-07 10:21:08.386271

"""

# revision identifiers, used by Alembic.
revision = '1a88eba5f47'
down_revision = '207a3173bf8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'userSignatures',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=False),
        sa.Column('systemId', sa.Integer, primary_key=True, autoincrement=False),
        sa.Column('data', sa.Text, nullable=False),
    )

    op.create_table(
        'corpSignatures',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=False),
        sa.Column('systemId', sa.Integer, primary_key=True, autoincrement=False),
        sa.Column('data', sa.Text, nullable=False),
    )


def downgrade():
    op.drop_table('userSignatures')
    op.drop_table('corpSignatures')
