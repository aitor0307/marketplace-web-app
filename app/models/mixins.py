from datetime import datetime

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON

from app.extensions import db

# JSONB on Postgres (where the app actually runs); plain JSON everywhere
# else so the sqlite-backed test config doesn't need a real Postgres to
# create tables against.
ExternalDataType = JSON().with_variant(JSONB, "postgresql")


class CRUDMixin:
    """Common primary key, audit columns, and CRUD helpers for every model.

    Every model gets:
      - ``id``: integer primary key
      - ``timestamp``: set once, on creation
      - ``updated_timestamp``: refreshed on every update
      - ``external_data``: a JSONB bag for provider/vendor/import data that
        doesn't deserve its own column yet
    plus create/save/update/delete/get_by_id/get_all so route and service
    code never touches ``db.session`` directly.
    """

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_timestamp = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    external_data = db.Column(
        ExternalDataType, default=dict, nullable=False, server_default="{}"
    )

    @classmethod
    def create(cls, commit=True, **kwargs):
        instance = cls(**kwargs)
        return instance.save(commit=commit)

    def update(self, commit=True, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return self.save(commit=commit)

    def save(self, commit=True):
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        db.session.delete(self)
        if commit:
            db.session.commit()
        return self

    @classmethod
    def get_by_id(cls, record_id):
        try:
            record_id = int(record_id)
        except (TypeError, ValueError):
            return None
        return db.session.get(cls, record_id)

    @classmethod
    def get_all(cls):
        return cls.query.all()

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
