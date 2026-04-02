from flask import Blueprint, request, jsonify
from app.services.list_service import create_list, get_all_lists, update_list_item_quantity, get_list_items

from app.models import List

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from flask import send_file
import io



list_bp = Blueprint("list", __name__)

@list_bp.route("/lists", methods=["GET"])
def fetch_all_lists():
    """
    Get all lists
    """
    response, status = get_all_lists()
    return jsonify(response), status


@list_bp.route("/lists", methods=["POST"])
def create_new_list():
    data = request.get_json()
    name = data.get("name")
    if not name:
        return jsonify({"error": "List name is required"}), 400

    response, status = create_list(name)
    return jsonify(response), status


@list_bp.route("/lists/<int:list_id>", methods=["GET"])
def fetch_list_items(list_id):
    response, status = get_list_items(list_id)
    return jsonify(response), status


@list_bp.route("/lists/item/<int:list_item_id>", methods=["PUT"])
def update_item_quantity(list_item_id):
    data = request.get_json()
    quantity = data.get("quantity")
    if quantity is None:
        return jsonify({"error": "Quantity is required"}), 400

    response, status = update_list_item_quantity(list_item_id, quantity)
    return jsonify(response), status




@list_bp.route("/lists/<int:list_id>/export", methods=["GET"])
def export_list_pdf(list_id):
    list_obj = List.query.get(list_id)
    if not list_obj:
        return {"error": "List not found"}, 404

    buffer = io.BytesIO()

    # Create PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()

    # 🔹 Title
    title = Paragraph(f"<b>Product List: {list_obj.name}</b>", styles["Title"])
    elements.append(title)
    elements.append(Spacer(1, 20))

    # 🔹 Table data (header + rows)
    data = [
        ["Product Name", "Barcode", "Quantity", "Added By"]
    ]

    for item in list_obj.items:
        data.append([
            item.product.name,
            item.product.barcode,
            str(item.quantity),
            item.user.username if item.user else "N/A"
        ])

    # 🔹 Create table
    table = Table(data, colWidths=[150, 150, 80, 120])

    # 🔹 Styling
    table.setStyle(TableStyle([
        # Header style
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),

        # Body style
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),

        # Grid lines (borders)
        ("GRID", (0, 0), (-1, -1), 1, colors.black),

        # Padding
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))

    elements.append(table)

    # Build PDF
    doc.build(elements)

    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"{list_obj.name}.pdf",
        mimetype="application/pdf"
    )