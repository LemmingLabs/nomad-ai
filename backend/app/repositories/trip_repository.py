from sqlalchemy.orm import Session

from app.models.trip import Trip


def create_trip(db: Session, **trip_data) -> Trip:
    trip = Trip(**trip_data)
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


def get_trip_by_id(db: Session, trip_id: int) -> Trip | None:
    return db.query(Trip).filter(Trip.id == trip_id).first()


def get_user_trips(db: Session, user_id: int) -> list[Trip]:
    return (
        db.query(Trip)
        .filter(Trip.user_id == user_id)
        .order_by(Trip.created_at.desc())
        .all()
    )


def update_trip(db: Session, trip: Trip, **updates) -> Trip:
    for key, value in updates.items():
        setattr(trip, key, value)
    db.commit()
    db.refresh(trip)
    return trip


def assign_trip_to_user(db: Session, trip: Trip, user_id: int) -> Trip:
    trip.user_id = user_id
    db.commit()
    db.refresh(trip)
    return trip


def delete_trip(db: Session, trip: Trip) -> None:
    db.delete(trip)
    db.commit()