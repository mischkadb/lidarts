"""empty message

Revision ID: 57e60c14fab7
Revises: 2c2c14f24f76
Create Date: 2018-06-09 13:23:40.916293

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '57e60c14fab7'
down_revision = '2c2c14f24f76'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('last_seen_ingame', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'last_seen_ingame')
    # ### end Alembic commands ###
