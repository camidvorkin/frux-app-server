"""Califications

Revision ID: 4b8ee581a176
Revises: c87f5a0d80bc
Create Date: 2021-07-10 15:23:21.976194

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4b8ee581a176'
down_revision = 'c87f5a0d80bc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('calification',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=True),
    sa.Column('puntuation', sa.Float(), nullable=True),
    sa.Column('review', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('calification')
    # ### end Alembic commands ###