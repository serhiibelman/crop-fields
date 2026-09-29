"""create fields table

Revision ID: 0001
Revises:
Create Date: 2026-09-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from geoalchemy2 import Geometry

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    op.create_table(
        "fields",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("crop", sa.String(100), nullable=False),
        sa.Column("owner", sa.String(255), nullable=False),
        sa.Column(
            "geom",
            Geometry("POLYGON", srid=4326, spatial_index=False),
            nullable=False,
        ),
        sa.Column(
            "area_ha",
            sa.Float(),
            sa.Computed("ST_Area(geom::geography) / 10000", persisted=True),
            nullable=False,
        ),
        sa.Column(
            "centroid",
            Geometry("POINT", srid=4326, spatial_index=False),
            sa.Computed("ST_Centroid(geom)", persisted=True),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_fields")),
        sa.CheckConstraint("ST_IsValid(geom)", name=op.f("ck_fields_geom_valid")),
        sa.CheckConstraint("area_ha > 0.1", name=op.f("ck_fields_min_area")),
    )

    op.create_index("ix_fields_geom", "fields", ["geom"], postgresql_using="gist")
    op.create_index(op.f("ix_fields_crop"), "fields", ["crop"])
    op.create_index(op.f("ix_fields_owner"), "fields", ["owner"])
    op.create_index(op.f("ix_fields_area_ha"), "fields", ["area_ha"])


def downgrade() -> None:
    # Indexes and constraints go with the table; the postgis extension is left in place
    # since other schemas may depend on it.
    op.drop_table("fields")
