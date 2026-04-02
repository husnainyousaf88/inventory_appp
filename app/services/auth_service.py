from app.models import User
from app.extensions import db
from flask_jwt_extended import create_access_token

SECRET_KEY = "your-secret-key"  # replace with .env value

def register_user(username, password):
    if User.query.filter_by(username=username).first():
        return {"error": "Username already exists"}, 400

    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return {"message": "User registered successfully"}, 201


def login_user(username, password):
    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return {"error": "Invalid username or password"}, 401

    # ✅ Convert to string
    token = create_access_token(identity=str(user.id))

    return {
        "token": token,
        "user_id": user.id,
        "username": user.username
    }, 200