"""empty message

Revision ID: ecf5786bc002
Revises: d5e83d0242cb
Create Date: 2023-01-12 18:16:26.628676

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "ecf5786bc002"
down_revision = "d5e83d0242cb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, "Project", "User", ["created_by_id"], ["id"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "Project", type_="foreignkey")
    # ### end Alembic commands ###