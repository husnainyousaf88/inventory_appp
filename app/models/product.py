from app.extensions import db

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    barcode = db.Column(db.String(100), unique=True, nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())