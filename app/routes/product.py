from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.product import Product

product_bp = Blueprint("product", __name__)


@product_bp.route("/products", methods=["POST"])
def create_product():
    data = request.get_json()

    name = data.get("name")
    barcode = data.get("barcode")

    if not name or not barcode:
        return {"error": "Name and barcode are required"}, 400

    existing = Product.query.filter_by(barcode=barcode).first()
    if existing:
        return {"error": "Product with this barcode already exists"}, 400

    product = Product(name=name, barcode=barcode)
    db.session.add(product)
    db.session.commit()

    return {
        "id": product.id,
        "name": product.name,
        "barcode": product.barcode
    }, 201


@product_bp.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    data = request.get_json()

    product = Product.query.get(product_id)
    if not product:
        return {"error": "Product not found"}, 404

    name = data.get("name")
    barcode = data.get("barcode")

    if name:
        product.name = name

    if barcode:
        # prevent duplicate barcode
        existing = Product.query.filter_by(barcode=barcode).first()
        if existing and existing.id != product_id:
            return {"error": "Barcode already used"}, 400
        product.barcode = barcode

    db.session.commit()

    return {
        "id": product.id,
        "name": product.name,
        "barcode": product.barcode
    }


@product_bp.route("/products", methods=["GET"])
def get_products():
    search = request.args.get("search", "")

    query = Product.query

    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    products = query.order_by(Product.id.desc()).all()

    return {
        "products": [
            {
                "id": p.id,
                "name": p.name,
                "barcode": p.barcode
            }
            for p in products
        ]
    }