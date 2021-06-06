"""Add category as a table

Revision ID: ec0ab2755014
Revises: 5bbe78b231dd
Create Date: 2021-06-06 12:50:29.904595

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ec0ab2755014'
down_revision = '5bbe78b231dd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    category_table = op.create_table('category',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('name')
    )

    op.bulk_insert(category_table, [
        {
            'name': 'Art',
            'description': 'Discover the artists and organizations who realize ambitious projects in visual art and performance.'
        },
        {
            'name': 'Books',
            'description': 'Explore fantastical worlds and original characters.'
        },
        {
            'name': 'Tech',
            'description': 'From fine design to innovative tech, discover projects from creators working to build a more beautiful future.'
        },
        {
            'name': 'Film',
            'description': 'Join forces with the intrepid filmmakers and festival creators changing the way stories get told on screen.'
        },
        {
            'name': 'Food',
            'description': 'See artisans and entrepreneurs breaking new ground in food.'
        },
        {
            'name': 'Games',
            'description': 'From tabletop adventures to beloved revivals, discover the projects forging the future of gameplay.'
        },
        {
            'name': 'Music',
            'description': 'Discover new albums, performances, and independent venues who shape the future of sound.'
        },
        {
            'name': 'Other',
            'description': 'Find interesting and varied projects while learning something new about our world.'
        }
    ])
    with op.batch_alter_table('project', schema=None) as batch_op:
        batch_op.add_column(sa.Column('category_name', sa.String(), nullable=True, default='Other'))
        batch_op.create_foreign_key(None, 'category', ['category_name'], ['name'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('project', schema=None) as batch_op:
        # batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('category_name')

    op.drop_table('category')
    # ### end Alembic commands ###
