from app.extensions import db
from app.models import Product, ListItem


def handle_scan(barcode, list_id, quantity=1, user_id=None):
    # 🔹 Try to find product
    product = Product.query.filter_by(barcode=barcode).first()

    # 🔹 If not found → create new product
    if not product:
        product = Product(
            name="New Item",
            barcode=barcode
        )
        db.session.add(product)
        db.session.commit()

    # 🔹 Check if already added to list
    existing_item = ListItem.query.filter_by(
        list_id=list_id,
        product_id=product.id
    ).first()

    if existing_item:
        return {
            "error": f"Product '{product.name}' already added to this list"
        }, 400

    # 🔹 Add to list
    new_item = ListItem(
        list_id=list_id,
        product_id=product.id,
        quantity=quantity,
        user_id=user_id
    )

    db.session.add(new_item)
    db.session.commit()

    return {
        "message": "Product added to list",
        "product": product.name,
        "barcode": product.barcode,
        "quantity": new_item.quantity,
        "added_by_user_id": user_id,
        "is_new_product": product.name == "New Item"
    }, 201