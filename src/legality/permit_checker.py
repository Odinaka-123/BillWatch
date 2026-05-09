from sqlalchemy import create_engine, Column, String, Float, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from pathlib import Path
from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger("permit_checker")

Base = declarative_base()
DB_PATH = Path(config["legality"]["permit_db"])
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
Session = sessionmaker(bind=engine)


class Permit(Base):
    __tablename__ = "permits"

    permit_id   = Column(String, primary_key=True)
    owner       = Column(String)
    lat         = Column(Float)
    lon         = Column(Float)
    address     = Column(String)
    area_m2     = Column(Float)
    valid_until = Column(DateTime)
    active      = Column(Boolean, default=True)


def init_db():
    Base.metadata.create_all(engine)
    logger.info("Permit database initialized.")


def check_permit(lat: float, lon: float, radius_deg: float = 0.0005) -> dict:
    session = Session()
    try:
        permits = session.query(Permit).filter(
            Permit.lat.between(lat - radius_deg, lat + radius_deg),
            Permit.lon.between(lon - radius_deg, lon + radius_deg),
            Permit.active == True,
            Permit.valid_until >= datetime.utcnow()
        ).all()

        if permits:
            p = permits[0]
            logger.info(f"Valid permit found: {p.permit_id}")
            return {
                "has_permit": True,
                "permit_id": p.permit_id,
                "owner": p.owner,
                "valid_until": str(p.valid_until)
            }

        logger.info(f"No valid permit at ({lat}, {lon})")
        return {"has_permit": False, "permit_id": None, "owner": None}

    except Exception as e:
        logger.error(f"Permit check failed: {e}")
        return {"has_permit": False, "permit_id": None, "owner": None}
    finally:
        session.close()


def add_permit(permit_id, owner, lat, lon, address, area_m2, valid_until):
    session = Session()
    try:
        p = Permit(
            permit_id=permit_id,
            owner=owner,
            lat=lat,
            lon=lon,
            address=address,
            area_m2=area_m2,
            valid_until=valid_until,
            active=True
        )
        session.add(p)
        session.commit()
        logger.info(f"Permit {permit_id} added.")
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to add permit: {e}")
    finally:
        session.close()