"""add registration_number to user

Revision ID: d7e8f9a1b2c3
Revises: c60439923ebd
Create Date: 2025-12-08 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd7e8f9a1b2c3'
down_revision = 'c60439923ebd'
branch_labels = None
depends_on = None


def upgrade():
    # Add registration_number column to user table
    op.add_column('user', sa.Column('registration_number', sa.String(length=50), nullable=True))
    
    # Add unique constraint
    op.create_unique_constraint('uq_user_registration_number', 'user', ['registration_number'])


def downgrade():
    # Remove unique constraint
    op.drop_constraint('uq_user_registration_number', 'user', type_='unique')
    
    # Remove column
    op.drop_column('user', 'registration_number')
