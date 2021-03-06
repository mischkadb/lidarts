"""empty message

Revision ID: c5ab287856d6
Revises: 6ccb2d66fe64
Create Date: 2020-04-14 12:47:19.891861

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c5ab287856d6'
down_revision = '6ccb2d66fe64'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('webcam_settings', sa.Column('latest_jitsi_hashid', sa.String(length=10), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('webcam_settings', 'latest_jitsi_hashid')
    # ### end Alembic commands ###
