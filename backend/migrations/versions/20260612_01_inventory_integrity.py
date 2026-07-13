"""Protect inventory integrity and correct outbound foreign key.

Revision ID: 20260612_01
Revises:
Create Date: 2026-06-12
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260612_01"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _has_unique_key(inspector, table_name: str, columns: list[str]) -> bool:
    expected = tuple(columns)
    constraints = inspector.get_unique_constraints(table_name)
    indexes = inspector.get_indexes(table_name)

    return any(
        tuple(item.get("column_names") or ()) == expected
        for item in [*constraints, *indexes]
        if item.get("unique", True)
    )


def _assert_no_duplicates(table_name: str, columns: list[str]) -> None:
    bind = op.get_bind()
    column_sql = ", ".join(f"`{column}`" for column in columns)
    duplicate = bind.execute(
        sa.text(
            f"SELECT {column_sql}, COUNT(*) AS duplicate_count "
            f"FROM `{table_name}` GROUP BY {column_sql} "
            "HAVING COUNT(*) > 1 LIMIT 1"
        )
    ).first()

    if duplicate:
        raise RuntimeError(
            f"Cannot add unique constraint to {table_name}({column_sql}): "
            "duplicate rows exist. Merge the duplicate rows and rerun the migration."
        )


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("inventories") and not _has_unique_key(
        inspector, "inventories", ["product_id", "location_id"]
    ):
        _assert_no_duplicates("inventories", ["product_id", "location_id"])
        op.create_unique_constraint(
            "uq_inventory_product_location",
            "inventories",
            ["product_id", "location_id"],
        )

    inspector = sa.inspect(bind)
    if inspector.has_table("locations") and not _has_unique_key(
        inspector, "locations", ["location_name", "zone"]
    ):
        _assert_no_duplicates("locations", ["location_name", "zone"])
        op.create_unique_constraint(
            "uq_location_name_zone",
            "locations",
            ["location_name", "zone"],
        )

    inspector = sa.inspect(bind)
    if not inspector.has_table("outbounds") or not inspector.has_table("products"):
        return

    product_foreign_keys = [
        foreign_key
        for foreign_key in inspector.get_foreign_keys("outbounds")
        if foreign_key.get("constrained_columns") == ["product_id"]
    ]

    has_correct_product_foreign_key = any(
        foreign_key.get("referred_table") == "products"
        and foreign_key.get("referred_columns") == ["product_id"]
        for foreign_key in product_foreign_keys
    )

    if not has_correct_product_foreign_key:
        for foreign_key in product_foreign_keys:
            if foreign_key.get("name"):
                op.drop_constraint(
                    foreign_key["name"], "outbounds", type_="foreignkey"
                )

        op.create_foreign_key(
            "fk_outbounds_product_id",
            "outbounds",
            "products",
            ["product_id"],
            ["product_id"],
        )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())

    if inspector.has_table("outbounds") and inspector.has_table("locations"):
        op.drop_constraint(
            "fk_outbounds_product_id", "outbounds", type_="foreignkey"
        )
        op.create_foreign_key(
            "fk_outbounds_product_id_locations",
            "outbounds",
            "locations",
            ["product_id"],
            ["location_id"],
        )

    if inspector.has_table("locations"):
        op.drop_constraint(
            "uq_location_name_zone", "locations", type_="unique"
        )

    if inspector.has_table("inventories"):
        op.drop_constraint(
            "uq_inventory_product_location", "inventories", type_="unique"
        )
