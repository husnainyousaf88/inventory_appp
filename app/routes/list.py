from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.services.list_service import create_list, get_all_lists, update_list_item_quantity, get_list_items, delete_list_item

from app.models import List

from flask import send_file

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
import io

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle


list_bp = Blueprint("list", __name__)

@list_bp.route("/lists", methods=["GET"])
@jwt_required()
def fetch_all_lists():
    """
    Get all lists
    """
    response, status = get_all_lists()
    return jsonify(response), status


@list_bp.route("/lists", methods=["POST"])
@jwt_required()
def create_new_list():
    data = request.get_json()
    name = data.get("name")
    if not name:
        return jsonify({"error": "List name is required"}), 400

    response, status = create_list(name)
    return jsonify(response), status


@list_bp.route("/lists/<int:list_id>", methods=["GET"])
@jwt_required()
def fetch_list_items(list_id):
    response, status = get_list_items(list_id)
    return jsonify(response), status


@list_bp.route("/lists/item/<int:list_item_id>", methods=["PUT"])
@jwt_required()
def update_item_quantity(list_item_id):
    data = request.get_json()
    quantity = data.get("quantity")
    if quantity is None:
        return jsonify({"error": "Quantity is required"}), 400

    response, status = update_list_item_quantity(list_item_id, quantity)
    return jsonify(response), status


@list_bp.route("/lists/<int:list_id>/items/<int:product_id>", methods=["DELETE"])
@jwt_required()
def remove_item(list_id, product_id):
    return delete_list_item(list_id, product_id)


@list_bp.route("/lists/<int:list_id>/export", methods=["GET"])
@jwt_required()
def export_list_pdf(list_id):
    list_obj = List.query.get(list_id)
    if not list_obj:
        return {"error": "List not found"}, 404

    buffer = io.BytesIO()

    # 🔥 Reduce margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=20,
        bottomMargin=20,
        leftMargin=20,
        rightMargin=20
    )

    elements = []
    styles = getSampleStyleSheet()

    centered_title_style = ParagraphStyle(
        name="CenteredTitle",
        parent=styles["Heading2"],
        alignment=TA_CENTER  # 🔥 this centers it
    )

    elements.append(Paragraph(f"<b>{list_obj.name} - {list_obj.created_at.date()}</b>", centered_title_style))

    items = list_obj.items
    chunk_size = 40  # 🔥 target 20 per page

    for i in range(0, len(items), chunk_size):
        chunk = items[i:i + chunk_size]

        # data = [["#", "Product", "Barcode", "Qty", "User", "Scan"]]
        data = [["#", "Product", "Barcode", "Qty", "User"]]

        for idx, item in enumerate(chunk, start=i + 1):
            # 🔥 Smaller barcode
            # barcode_img = barcode_drawing(
            #     value=item.product.barcode
            # )

            data.append([
                str(idx),
                item.product.name[:30],  # trim long names
                item.product.barcode,
                str(item.quantity),
                item.user.username if item.user else "-",
                # barcode_img
            ])

        # 🔥 Adjust widths to fit page better
        table = Table(data, colWidths=[40, 150, 150, 40, 150])

        table.setStyle(TableStyle([
            # Header
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),  # 🔥 smaller font

            # Grid
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),

            # Alignment
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("ALIGN", (1, 1), (1, -1), "LEFT"),

            # 🔥 Reduce padding (key fix)
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),

            # Row color
            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
        ]))

        elements.append(table)

        if i + chunk_size < len(items):
            elements.append(PageBreak())

    doc.build(elements)

    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"{list_obj.name}.pdf",
        mimetype="application/pdf"
    )