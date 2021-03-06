"""empty message

Revision ID: 7b2abde71e5b
Revises: f03586cb5f2e
Create Date: 2018-01-29 13:43:29.313980

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7b2abde71e5b'
down_revision = 'f03586cb5f2e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_tokens',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('token_string', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_tokens_token_string'), 'user_tokens', ['token_string'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_tokens_token_string'), table_name='user_tokens')
    op.drop_table('user_tokens')
    # ### end Alembic commands ###
