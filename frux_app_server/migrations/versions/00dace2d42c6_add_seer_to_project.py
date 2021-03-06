"""Add Seer to project

Revision ID: 00dace2d42c6
Revises: e6be07ed5a99
Create Date: 2021-07-05 18:26:32.150137

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '00dace2d42c6'
down_revision = 'e6be07ed5a99'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('project', schema=None) as batch_op:
        batch_op.add_column(sa.Column('has_seer', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('project', schema=None) as batch_op:
        batch_op.drop_column('has_seer')

    # ### end Alembic commands ###
