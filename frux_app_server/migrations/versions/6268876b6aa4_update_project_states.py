"""Update project states

Revision ID: 6268876b6aa4
Revises: 10c82e59b015
Create Date: 2021-07-06 22:56:59.352191

"""
from alembic import op
import sqlalchemy as sa


old_options = ('CREATED', 'IN_PROGRESS', 'COMPLETE')
new_options = sorted(old_options + ('FUNDING', 'CANCELED'))

old_type = sa.Enum(*old_options, name='state')
new_type = sa.Enum(*new_options, name='state')
tmp_type = sa.Enum(*new_options, name='_state')

tcr = sa.sql.table('project',
                   sa.Column('current_state', new_type, nullable=False))


# revision identifiers, used by Alembic.
revision = '6268876b6aa4'
down_revision = '10c82e59b015'
branch_labels = None
depends_on = None


def upgrade():
    # Create a tempoary "_state" type, convert and drop the "old" type
    tmp_type.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE project ALTER COLUMN current_state TYPE _state'
               ' USING current_state::text::_state')
    old_type.drop(op.get_bind(), checkfirst=False)
    # Create and convert to the "new" state type
    new_type.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE project ALTER COLUMN current_state TYPE state'
               ' USING current_state::text::state')
    tmp_type.drop(op.get_bind(), checkfirst=False)


def downgrade():
    # Convert 'FUNDING' state into 'IN_PROGRESS'
    op.execute(tcr.update().where(tcr.c.current_state==u'FUNDING')
               .values(current_state='IN_PROGRESS'))
    # Convert 'CANCELED' state into 'IN_PROGRESS'
    op.execute(tcr.update().where(tcr.c.current_state==u'CANCELED')
               .values(current_state='IN_PROGRESS'))
    # Create a tempoary "_state" type, convert and drop the "new" type
    tmp_type.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE project ALTER COLUMN current_state TYPE _state'
               ' USING current_state::text::_state')
    new_type.drop(op.get_bind(), checkfirst=False)
    # Create and convert to the "old" state type
    old_type.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE project ALTER COLUMN current_state TYPE state'
               ' USING current_state::text::state')
    tmp_type.drop(op.get_bind(), checkfirst=False)