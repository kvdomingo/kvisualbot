"""add vlive model

Revision ID: 5c6b26f1c575
Revises: 75f440481a2a
Create Date: 2020-07-17 21:00:54.648359+08:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5c6b26f1c575'
down_revision = '75f440481a2a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('vliveaccount',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('channel_code', sa.String(length=255), nullable=True),
    sa.Column('channel_seq', sa.BigInteger(), nullable=True),
    sa.Column('last_video_seq', sa.BigInteger(), nullable=True),
    sa.Column('group_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['group.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('vliveaccount')
    # ### end Alembic commands ###