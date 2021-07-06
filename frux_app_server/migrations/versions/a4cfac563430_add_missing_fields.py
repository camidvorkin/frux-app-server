"""Add missing fields

Revision ID: a4cfac563430
Revises: 00dace2d42c6
Create Date: 2021-07-06 02:33:23.534490

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a4cfac563430'
down_revision = '00dace2d42c6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('project', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_seer', sa.Boolean(), nullable=True))
        batch_op.drop_column('has_seer')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('has_seer', sa.BOOLEAN(), autoincrement=False, nullable=True))
        batch_op.drop_column('is_seer')

    with op.batch_alter_table('project', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###
