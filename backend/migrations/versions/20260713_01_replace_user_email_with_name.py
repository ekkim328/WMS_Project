"""Replace user email with display name.

Revision ID: 20260713_01
Revises: 20260612_01
Create Date: 2026-07-13
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260713_01"
down_revision: str | None = "20260612_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _column_names() -> set[str]:
    inspector = sa.inspect(op.get_bind())
    if not inspector.has_table("users"):
        return set()
    return {column["name"] for column in inspector.get_columns("users")}


def upgrade() -> None:
    columns = _column_names()
    if not columns:
        return

    if "name" not in columns:
        op.add_column("users", sa.Column("name", sa.String(length=100), nullable=True))
        op.execute(sa.text("UPDATE users SET name = username WHERE name IS NULL"))
        op.alter_column(
            "users",
            "name",
            existing_type=sa.String(length=100),
            nullable=False,
        )

    if "email" in columns:
        op.drop_column("users", "email")


def downgrade() -> None:
    columns = _column_names()
    if not columns:
        return

    if "email" not in columns:
        op.add_column("users", sa.Column("email", sa.String(length=100), nullable=True))
        op.execute(
            sa.text(
                "UPDATE users SET email = CONCAT(username, '@example.invalid') "
                "WHERE email IS NULL"
            )
        )
        op.alter_column(
            "users",
            "email",
            existing_type=sa.String(length=100),
            nullable=False,
        )
        op.create_unique_constraint("uq_users_email", "users", ["email"])

    if "name" in columns:
        op.drop_column("users", "name")
