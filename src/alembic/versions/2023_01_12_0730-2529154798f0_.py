"""empty message

Revision ID: 2529154798f0
Revises: 40068ac95f4d
Create Date: 2023-01-12 07:30:34.734815

"""
import sqlalchemy as sa
import sqlmodel  # added
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "2529154798f0"
down_revision = "40068ac95f4d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "ProjectUserLink",
        sa.Column("project_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("user_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("joined_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["Project.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["User.id"],
        ),
        sa.PrimaryKeyConstraint("project_id", "user_id"),
    )
    op.drop_table("ProjectUsersLink")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "ProjectUsersLink",
        sa.Column("project_id", postgresql.UUID(), autoincrement=False, nullable=False),
        sa.Column("user_id", postgresql.UUID(), autoincrement=False, nullable=False),
        sa.Column("joined_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(
            ["project_id"], ["Project.id"], name="ProjectUsersLink_project_id_fkey"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["User.id"], name="ProjectUsersLink_user_id_fkey"),
        sa.PrimaryKeyConstraint("project_id", "user_id", name="ProjectUsersLink_pkey"),
    )
    op.drop_table("ProjectUserLink")
    # ### end Alembic commands ###
