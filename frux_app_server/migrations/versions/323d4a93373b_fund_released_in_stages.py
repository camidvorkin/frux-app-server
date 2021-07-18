"""Fund released in stages

Revision ID: 323d4a93373b
Revises: c76968c1c20b
Create Date: 2021-07-16 18:10:41.015626

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '323d4a93373b'
down_revision = 'c76968c1c20b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('project_stage', schema=None) as batch_op:
        batch_op.add_column(sa.Column('funds_released', sa.Boolean(), default=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('project_stage', schema=None) as batch_op:
        batch_op.drop_column('funds_released')

    # ### end Alembic commands ###
