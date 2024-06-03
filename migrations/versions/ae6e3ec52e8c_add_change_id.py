"""add change_id

Revision ID: ae6e3ec52e8c
Revises: 555118bf76f8
Create Date: 2024-05-30 14:26:05.448856

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ae6e3ec52e8c'
down_revision = '555118bf76f8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('delivery_order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('change_id', sa.String(length=36), nullable=True))

    with op.batch_alter_table('money', schema=None) as batch_op:
        batch_op.add_column(sa.Column('change_id', sa.String(length=36), nullable=True))

    with op.batch_alter_table('payment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('change_id', sa.String(length=36), nullable=True))

    with op.batch_alter_table('purchase_event', schema=None) as batch_op:
        batch_op.add_column(sa.Column('change_id', sa.String(length=36), nullable=True))

    with op.batch_alter_table('purchase_order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('change_id', sa.String(length=36), nullable=True))

    with op.batch_alter_table('purchase_order_line', schema=None) as batch_op:
        batch_op.add_column(sa.Column('change_id', sa.String(length=36), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('purchase_order_line', schema=None) as batch_op:
        batch_op.drop_column('change_id')

    with op.batch_alter_table('purchase_order', schema=None) as batch_op:
        batch_op.drop_column('change_id')

    with op.batch_alter_table('purchase_event', schema=None) as batch_op:
        batch_op.drop_column('change_id')

    with op.batch_alter_table('payment', schema=None) as batch_op:
        batch_op.drop_column('change_id')

    with op.batch_alter_table('money', schema=None) as batch_op:
        batch_op.drop_column('change_id')

    with op.batch_alter_table('delivery_order', schema=None) as batch_op:
        batch_op.drop_column('change_id')

    # ### end Alembic commands ###
