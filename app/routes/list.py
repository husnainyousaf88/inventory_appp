from flask import Blueprint, request, jsonify
from app.services.list_service import create_list, get_all_lists, update_list_item_quantity, get_list_items

from app.models import List

from flask import send_file


from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph, PageBreak
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
import io
from app.utils.helpers import barcode_drawing



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
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph(f"<b>Product List: {list_obj.name}</b>", styles["Title"]))
    elements.append(Spacer(1, 20))

    items = list_obj.items
    chunk_size = 40

    for i in range(0, len(items), chunk_size):
        chunk = items[i:i + chunk_size]

        # Header
        data = [["#", "Product Name", "Barcode", "Qty", "Added By", "Scan Code"]]

        for idx, item in enumerate(chunk, start=i + 1):
            barcode_img = barcode_drawing(value=item.product.barcode)
            data.append([
                str(idx),
                item.product.name,
                item.product.barcode,
                str(item.quantity),
                item.user.username if item.user else "N/A",
                barcode_img
            ])

        table = Table(data, colWidths=[30, 140, 100, 30, 150])

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

            ("GRID", (0, 0), (-1, -1), 1, colors.black),

            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("ALIGN", (1, 1), (1, -1), "LEFT"),

            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
        ]))

        elements.append(table)

        # Add page break if more items remain
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