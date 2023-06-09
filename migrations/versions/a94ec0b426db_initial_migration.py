"""Initial migration.

Revision ID: a94ec0b426db
Revises: 
Create Date: 2023-04-22 14:27:43.799553

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a94ec0b426db'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('reading',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('trans_id', sa.String(length=120), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('rtd_1', sa.Float(), nullable=False),
    sa.Column('rtd_2', sa.Float(), nullable=False),
    sa.Column('order_num', sa.Integer(), nullable=False),
    sa.Column('requestor_id', sa.String(length=20), nullable=False),
    sa.Column('temp_1', sa.Float(), nullable=False),
    sa.Column('temp_2', sa.Float(), nullable=False),
    sa.Column('last_rrq', sa.Integer(), nullable=False),
    sa.Column('last_rrs', sa.Integer(), nullable=False),
    sa.Column('last_rx', sa.Integer(), nullable=False),
    sa.Column('last_tx', sa.Integer(), nullable=False),
    sa.Column('is_data_transmitted', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password', sa.String(length=128), nullable=False),
    sa.Column('firstname', sa.String(length=80), nullable=False),
    sa.Column('lastname', sa.String(length=80), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    op.drop_table('reading')
    # ### end Alembic commands ###
