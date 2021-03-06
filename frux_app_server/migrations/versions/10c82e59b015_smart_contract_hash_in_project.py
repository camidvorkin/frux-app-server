"""Smart contract hash in project

Revision ID: 10c82e59b015
Revises: 5a4d2b1515c6
Create Date: 2021-07-06 19:47:59.710889

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '10c82e59b015'
down_revision = '5a4d2b1515c6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('project', schema=None) as batch_op:
        batch_op.add_column(sa.Column('smart_contract_hash', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('project', schema=None) as batch_op:
        batch_op.drop_column('smart_contract_hash')

    # ### end Alembic commands ###
