from app.extensions import db
from app.models.list_item import ListItem

class List(db.Model):
    __tablename__ = "lists"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Relationship to list items
    items = db.relationship(
        "ListItem",
        back_populates="list",
        cascade="all, delete-orphan"
    )