"""Update models

Revision ID: 172c7a717cb7
Revises: 98bdf2c16ff5
Create Date: 2025-01-09 06:03:35.819474

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '172c7a717cb7'
down_revision: Union[str, None] = '98bdf2c16ff5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('external_id', sa.String(), nullable=False))
    op.alter_column('user', 'joined_dt',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=sa.DateTime(),
               existing_nullable=False,
               existing_server_default=sa.text('now()'))
    op.alter_column('user', 'last_login_dt',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=sa.DateTime(),
               nullable=False)
    op.alter_column('user', 'profile_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.create_index('ix_external_id_provider', 'user', ['external_id', 'provider'], unique=True)
    op.drop_column('user', 'is_superuser')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('is_superuser', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.drop_index('ix_external_id_provider', table_name='user')
    op.alter_column('user', 'profile_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('user', 'last_login_dt',
               existing_type=sa.DateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               nullable=True)
    op.alter_column('user', 'joined_dt',
               existing_type=sa.DateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=False,
               existing_server_default=sa.text('now()'))
    op.drop_column('user', 'external_id')
    # ### end Alembic commands ###
