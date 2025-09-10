"""update_employee_skills_to_json

Revision ID: 1ce7b8465b0a
Revises: a04634242879
Create Date: 2025-07-24 00:43:36.856077

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1ce7b8465b0a'
down_revision: Union[str, Sequence[str], None] = 'a04634242879'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('employees', schema=None) as batch_op:
        batch_op.alter_column('status',
                   existing_type=sa.VARCHAR(length=10),
                   type_=sa.Enum('ACTIVE', 'INACTIVE', 'ON_LEAVE', 'ON_VACATION', 'TERMINATED', name='employeestatus'),
                   existing_nullable=False)
        batch_op.alter_column('skills',
                   existing_type=sa.TEXT(),
                   type_=sa.JSON(),
                   existing_nullable=True)
        batch_op.alter_column('certifications',
                   existing_type=sa.TEXT(),
                   type_=sa.JSON(),
                   existing_nullable=True)
        batch_op.alter_column('special_training',
                   existing_type=sa.TEXT(),
                   type_=sa.JSON(),
                   existing_nullable=True)

    with op.batch_alter_table('workloads', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_workload_employee_date', ['employee_id', 'date'])


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('workloads', schema=None) as batch_op:
        batch_op.drop_constraint('uq_workload_employee_date', type_='unique')

    with op.batch_alter_table('employees', schema=None) as batch_op:
        batch_op.alter_column('special_training',
                   existing_type=sa.JSON(),
                   type_=sa.TEXT(),
                   existing_nullable=True)
        batch_op.alter_column('certifications',
                   existing_type=sa.JSON(),
                   type_=sa.TEXT(),
                   existing_nullable=True)
        batch_op.alter_column('skills',
                   existing_type=sa.JSON(),
                   type_=sa.TEXT(),
                   existing_nullable=True)
        batch_op.alter_column('status',
                   existing_type=sa.Enum('ACTIVE', 'INACTIVE', 'ON_LEAVE', 'ON_VACATION', 'TERMINATED', name='employeestatus'),
                   type_=sa.VARCHAR(length=10),
                   existing_nullable=False)