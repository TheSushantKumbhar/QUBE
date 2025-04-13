"""drop live quiz tables

Revision ID: 190ddcec0aa6
Revises: 9eda72ae4703
Create Date: 2025-04-13 20:23:14.513866

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '190ddcec0aa6'
down_revision = '9eda72ae4703'
branch_labels = None
depends_on = None


# def upgrade():
#     op.drop_table('live_quiz_participants')
#     op.drop_table('live_quiz_rooms')

def upgrade():
    op.execute('DROP TABLE IF EXISTS live_quiz_participants CASCADE')
    op.execute('DROP TABLE IF EXISTS live_quiz_rooms CASCADE')



def downgrade():
    pass
