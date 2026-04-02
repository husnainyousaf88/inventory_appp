from app.extensions import db
from app.models import List, ListItem, Product, User


def create_list(name):
    new_list = List(name=name)
    db.session.add(new_list)
    db.session.commit()

    return {
        "id": new_list.id,
        "name": new_list.name,
        "created_at": new_list.created_at
    }, 201


def get_all_lists():
    """
    Fetch all lists
    """
    lists = List.query.order_by(List.created_at.desc()).all()

    result = []
    for l in lists:
        result.append({
            "id": l.id,
            "name": l.name,
            "created_at": l.created_at
        })

    return {"lists": result, "total_lists": len(result)}, 200

def get_list_items(list_id):
    list_obj = List.query.get(list_id)
    if not list_obj:
        return {"error": "List not found"}, 404

    items = (
        db.session.query(ListItem, Product)
        .join(Product, ListItem.product_id == Product.id)
        .filter(ListItem.list_id == list_id)
        .all()
    )

    result = []
    for item, product in items:
        result.append({
            "list_item_id": item.id,
            "product_id": product.id,
            "product_name": product.name,
            "barcode": product.barcode,
            "quantity": item.quantity,
            "user": item.user.username
        })

    return {
        "list_id": list_obj.id,
        "list_name": list_obj.name,
        "items": result,
        "total_items": len(result)
    }, 200


def update_list_item_quantity(list_item_id, quantity):
    """
    Update the quantity of a list item
    """
    item = ListItem.query.get(list_item_id)
    if not item:
        return {"error": "List item not found"}, 404

    if quantity < 1:
        return {"error": "Quantity must be at least 1"}, 400

    item.quantity = quantity
    db.session.commit()

    return {
        "message": "Quantity updated",
        "list_item_id": item.id,
        "product_id": item.product_id,
        "quantity": item.quantity
    }, 200