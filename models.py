from datetime import date

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Farm(Base):
    __tablename__ = "farms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    district: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    area_hectares: Mapped[float] = mapped_column(Float, nullable=False)
    crop_type: Mapped[str] = mapped_column(String(20), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    farmer_phone: Mapped[str] = mapped_column(String(30), nullable=False)
    soil_type: Mapped[str] = mapped_column(String(60), nullable=False)
    ndvi_records: Mapped[list["NDVIRecord"]] = relationship(back_populates="farm", cascade="all, delete-orphan")
    harvest_predictions: Mapped[list["HarvestPrediction"]] = relationship(back_populates="farm", cascade="all, delete-orphan")


class NDVIRecord(Base):
    __tablename__ = "ndvi_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey("farms.id"), nullable=False, index=True)
    recorded_date: Mapped[date] = mapped_column(Date, nullable=False)
    ndvi_value: Mapped[float] = mapped_column(Float, nullable=False)
    b4_red: Mapped[float] = mapped_column(Float, nullable=False)
    b8_nir: Mapped[float] = mapped_column(Float, nullable=False)
    farm: Mapped[Farm] = relationship(back_populates="ndvi_records")


class HarvestPrediction(Base):
    __tablename__ = "harvest_predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey("farms.id"), nullable=False, index=True)
    predicted_harvest_date: Mapped[date] = mapped_column(Date, nullable=False)
    confidence_days: Mapped[int] = mapped_column(Integer, nullable=False)
    is_high_confidence: Mapped[bool] = mapped_column(Boolean, nullable=False)
    farm: Mapped[Farm] = relationship(back_populates="harvest_predictions")


class MarketPrice(Base):
    __tablename__ = "market_prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    market_name: Mapped[str] = mapped_column(String(120), nullable=False)
    district: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    crop_type: Mapped[str] = mapped_column(String(20), nullable=False)
    price_per_quintal: Mapped[float] = mapped_column(Float, nullable=False)
    recorded_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)


class ColdStorage(Base):
    __tablename__ = "cold_storages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    district: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    capacity_tonnes: Mapped[float] = mapped_column(Float, nullable=False)
    cost_per_day_per_tonne: Mapped[float] = mapped_column(Float, nullable=False)
    crops_supported: Mapped[str] = mapped_column(String(100), nullable=False)
    contact_number: Mapped[str] = mapped_column(String(30), nullable=False)


class AlertSent(Base):
    __tablename__ = "alerts_sent"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    district: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    crop_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    oversupply_ratio: Mapped[float] = mapped_column(Float, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    alert_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    farmers_notified: Mapped[int] = mapped_column(Integer, nullable=False)
    action_taken: Mapped[str] = mapped_column(String(200), nullable=False)
