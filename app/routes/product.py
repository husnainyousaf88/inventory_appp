from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.product import Product
from sqlalchemy import or_
from flask_jwt_extended import jwt_required


product_bp = Blueprint("product", __name__)


@product_bp.route("/products", methods=["POST"])
@jwt_required()
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
@jwt_required()
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
@jwt_required()
def get_products():
    search = request.args.get("search", "")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))

    query = Product.query

    if search:
        query = query.filter(
            or_(
                Product.name.ilike(f"%{search}%"),
                Product.barcode.ilike(f"%{search}%")
            )
        )

    pagination = query.order_by(Product.id.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    products = pagination.items

    return {
        "products": [
            {
                "id": p.id,
                "name": p.name,
                "barcode": p.barcode
            }
            for p in products
        ],
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages
        }
    }


@product_bp.route("/products/<int:product_id>", methods=["DELETE"])
@jwt_required()
def delete_product(product_id):
    product = Product.query.get(product_id)

    if not product:
        return {"error": "Product not found"}, 404

    # Optional: check if product is used in any list
    if product.list_items:
        return {
            "error": "Cannot delete product. It is used in lists."
        }, 400

    db.session.delete(product)
    db.session.commit()

    return {"message": "Product deleted successfully"}, 200