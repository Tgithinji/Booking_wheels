"""users table

Revision ID: 0fe38ef10866
Revises: 
Create Date: 2024-05-20 12:42:20.260165

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0fe38ef10866'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_user_username'), ['username'], unique=True)

    op.create_table('car',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('make', sa.String(length=140), nullable=False),
    sa.Column('model', sa.String(length=140), nullable=False),
    sa.Column('year', sa.String(length=140), nullable=False),
    sa.Column('reg_num', sa.String(length=140), nullable=False),
    sa.Column('fuel_type', sa.String(length=140), nullable=False),
    sa.Column('mileage', sa.Integer(), nullable=False),
    sa.Column('seats', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=140), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('car', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_car_timestamp'), ['timestamp'], unique=False)

    op.create_table('booking',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=140), nullable=True),
    sa.Column('start_date', sa.DateTime(), nullable=True),
    sa.Column('end_date', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('car_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['car_id'], ['car.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('booking', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_booking_end_date'), ['end_date'], unique=False)
        batch_op.create_index(batch_op.f('ix_booking_start_date'), ['start_date'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('booking', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_booking_start_date'))
        batch_op.drop_index(batch_op.f('ix_booking_end_date'))

    op.drop_table('booking')
    with op.batch_alter_table('car', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_car_timestamp'))

    op.drop_table('car')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_username'))
        batch_op.drop_index(batch_op.f('ix_user_email'))

    op.drop_table('user')
    # ### end Alembic commands ###
