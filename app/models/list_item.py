from app.extensions import db
# from app.models.product import Product
# from app.models.list import List
# from app.models.user import User


class ListItem(db.Model):
    __tablename__ = "list_items"

    id = db.Column(db.Integer, primary_key=True)

    list_id = db.Column(db.Integer, db.ForeignKey("lists.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)  # Who added this product

    quantity = db.Column(db.Integer, default=1, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Relationships
    list = db.relationship("List", back_populates="items")
    product = db.relationship("Product")
    user = db.relationship("User")

    __table_args__ = (
        db.UniqueConstraint("list_id", "product_id", name="unique_list_product"),
    )