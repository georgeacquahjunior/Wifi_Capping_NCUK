from werkzeug.security import generate_password_hash
from sqlalchemy import text
from app import app, db
from datetime import datetime

def insert_admins():
    admins = [
        {"admin_id": "ADM001", "first_name": "Grace", "last_name": "Mensah", "password_hash": "adminpass1"},
        {"admin_id": "ADM002", "first_name": "Kwame", "last_name": "Owusu", "password_hash": "adminpass2"},
        {"admin_id": "ADM003", "first_name": "Akosua", "last_name": "Boateng", "password_hash": "adminpass3"},
        {"admin_id": "ADM004", "first_name": "Daniel", "last_name": "Asare", "password_hash": "adminpass4"},
        {"admin_id": "ADM005", "first_name": "Esi", "last_name": "Amoako", "password_hash": "adminpass5"},
    ]

    insert_query = text("""
        INSERT INTO admins (admin_id, first_name, last_name, password_hash, created_at)
        VALUES (:admin_id, :first_name, :last_name, :password_hash, :created_at)
    """)

    with app.app_context():
        for admin in admins:
            db.session.execute(insert_query, {
                "admin_id": admin["admin_id"],
                "first_name": admin["first_name"],
                "last_name": admin["last_name"],
                "password_hash": generate_password_hash(admin["password_hash"]),
                "created_at": datetime.utcnow()
            })
        db.session.commit()
        print("5 admins inserted successfully.")

if __name__ == "__main__":
    insert_admins()
