"""Add wallet to user

Revision ID: e591bdcc4de6
Revises: a4cfac563430
Create Date: 2021-06-26 20:43:53.509947

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e591bdcc4de6'
down_revision = 'a4cfac563430'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('wallet',
    sa.Column('address', sa.String(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('address')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('wallet_address', sa.String(), nullable=True))
        batch_op.create_foreign_key(None, 'wallet', ['wallet_address'], ['address'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        # batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('wallet_address')

    op.drop_table('wallet')
    # ### end Alembic commands ###
