"""Update flaskApp

Revision ID: fae9e545612d
Revises: 
Create Date: 2024-05-24 22:58:50.138730

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fae9e545612d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('nfcapp_commodity_item_odoo', schema=None) as batch_op:
        batch_op.add_column(sa.Column('write_date', sa.DateTime(), nullable=True))

    with op.batch_alter_table('purchase_order_line_odoo', schema=None) as batch_op:
        batch_op.add_column(sa.Column('write_date', sa.DateTime(), nullable=True))

    with op.batch_alter_table('purchase_order_odoo', schema=None) as batch_op:
        batch_op.add_column(sa.Column('write_date', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('purchase_order_odoo', schema=None) as batch_op:
        batch_op.drop_column('write_date')

    with op.batch_alter_table('purchase_order_line_odoo', schema=None) as batch_op:
        batch_op.drop_column('write_date')

    with op.batch_alter_table('nfcapp_commodity_item_odoo', schema=None) as batch_op:
        batch_op.drop_column('write_date')

    # ### end Alembic commands ###