from flask import Blueprint, request, jsonify
from app.services.scan_service import handle_scan
from flask_jwt_extended import jwt_required, get_jwt_identity

scan_bp = Blueprint("scan", __name__)



@scan_bp.route("/scan", methods=["POST"])
@jwt_required()
def scan():
    data = request.get_json()

    barcode = data.get("barcode")
    list_id = data.get("list_id")
    quantity = data.get("quantity", 1)

    # ✅ GET USER ID FROM TOKEN HERE
    user_id = int(get_jwt_identity())

    response, status = handle_scan(
        barcode,
        list_id,
        quantity,
        user_id=user_id
    )

    return jsonify(response), status