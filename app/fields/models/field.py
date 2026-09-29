import uuid
from datetime import datetime

from geoalchemy2 import Geometry, WKBElement
from sqlalchemy import CheckConstraint, Computed, DateTime, Float, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.models import Base


class Field(Base):
    __tablename__ = "fields"
    __table_args__ = (
        CheckConstraint("ST_IsValid(geom)", name="geom_valid"),
        CheckConstraint("area_ha > 0.1", name="min_area"),
        # GiST (R-tree over bounding boxes) — the index behind find-by-point.
        Index("ix_fields_geom", "geom", postgresql_using="gist"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, server_default=func.gen_random_uuid())
    name: Mapped[str] = mapped_column(String(255))
    crop: Mapped[str] = mapped_column(String(100), index=True)
    owner: Mapped[str] = mapped_column(String(255), index=True)
    # geometry (planar, degrees) rather than geography: faster index/predicates, and for
    # field-sized polygons the planar vs spherical edge difference is negligible.
    geom: Mapped[WKBElement] = mapped_column(
        Geometry("POLYGON", srid=4326, spatial_index=False),
    )
    # Area on the WGS84 spheroid, computed once on write so area filters hit a B-tree.
    area_ha: Mapped[float] = mapped_column(
        Float,
        Computed("ST_Area(geom::geography) / 10000", persisted=True),
        index=True,
    )
    centroid: Mapped[WKBElement] = mapped_column(
        Geometry("POINT", srid=4326, spatial_index=False),
        Computed("ST_Centroid(geom)", persisted=True),
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
