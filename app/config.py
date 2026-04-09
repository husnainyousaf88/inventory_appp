import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "postgres://postgres:newpassword@localhost/inventory_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False