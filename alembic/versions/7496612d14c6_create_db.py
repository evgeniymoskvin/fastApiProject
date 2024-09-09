"""'create_db'

Revision ID: 7496612d14c6
Revises: 
Create Date: 2024-09-09 08:32:28.814563

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7496612d14c6'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('groupsends',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bucket_name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('requests_number',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bucket_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['bucket_id'], ['groupsends.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('inboxfiles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('file_name', sa.String(), nullable=False),
    sa.Column('send_number_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['send_number_id'], ['requests_number.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('inboxfiles')
    op.drop_table('requests_number')
    op.drop_table('groupsends')
    # ### end Alembic commands ###