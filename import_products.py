import csv
from app import create_app
from app.extensions import db
from app.models.product import Product

import os
from dotenv import load_dotenv

load_dotenv()  # ✅ THIS LINE FIXES YOUR ISSUE

from app import create_app
from app.extensions import db
from app.models.product import Product

app = create_app()

print(os.getenv("DATABASE_URL"))

def import_csv(file_path):
    with app.app_context():
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            count = 0

            for row in reader:
                barcode = row.get("barcode")
                name = row.get("description") or "New Item"

                if not barcode:
                    continue

                # Avoid duplicates
                existing = Product.query.filter_by(barcode=barcode).first()
                if existing:
                    continue

                product = Product(
                    name=name,
                    barcode=barcode
                )

                db.session.add(product)
                count += 1

                # Commit in batches (important for performance)
                if count % 500 == 0:
                    db.session.commit()
                    print(f"{count} products inserted...")

            db.session.commit()
            print(f"✅ Done. Total inserted: {count}")


if __name__ == "__main__":
    import_csv("clean_output.csv")