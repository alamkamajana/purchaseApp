"""Update flaskApp

Revision ID: f44b6f7f47fd
Revises: abd154b66042
Create Date: 2024-05-28 09:49:08.252446

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f44b6f7f47fd'
down_revision = 'abd154b66042'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('purchase_event', schema=None) as batch_op:
        batch_op.add_column(sa.Column('fund', sa.Float(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('purchase_event', schema=None) as batch_op:
        batch_op.drop_column('fund')

    # ### end Alembic commands ###
