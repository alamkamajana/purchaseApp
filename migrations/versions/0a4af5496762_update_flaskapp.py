"""Update flaskApp

Revision ID: 0a4af5496762
Revises: 922db69db66e
Create Date: 2024-06-04 16:24:55.759397

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0a4af5496762'
down_revision = '922db69db66e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('delivery_order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sent_date', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('received_date', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('status', sa.String(length=64), nullable=True))
        batch_op.drop_column('date')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('delivery_order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date', sa.DATE(), nullable=True))
        batch_op.drop_column('status')
        batch_op.drop_column('received_date')
        batch_op.drop_column('sent_date')

    # ### end Alembic commands ###
