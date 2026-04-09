# in app/cli.py or __init__.py

import click
import csv
from app.extensions import db
from app.models.product import Product
from flask.cli import with_appcontext


@click.command("import-products")
@click.argument("file_path")
@with_appcontext
def import_products(file_path):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        count = 0

        for row in reader:
            barcode = row.get("barcode")
            name = row.get("description") or "New Item"

            if not barcode:
                continue

            if Product.query.filter_by(barcode=barcode).first():
                continue

            db.session.add(Product(name=name, barcode=barcode))
            count += 1

            if count % 500 == 0:
                db.session.commit()

        db.session.commit()
        print(f"Imported {count} products")