from werkzeug.security import generate_password_hash
from sqlalchemy import text
from app import app, db

def insert_admins():
    admins = [
        {"admin_id": "ADM001", "first_name": "Grace", "last_name": "Mensah", "password": "adminpass1"},
        {"admin_id": "ADM002", "first_name": "Kwame", "last_name": "Owusu", "password": "adminpass2"},
        {"admin_id": "ADM003", "first_name": "Akosua", "last_name": "Boateng", "password": "adminpass3"},
        {"admin_id": "ADM004", "first_name": "Daniel", "last_name": "Asare", "password": "adminpass4"},
        {"admin_id": "ADM005", "first_name": "Esi", "last_name": "Amoako", "password": "adminpass5"},
    ]

    insert_query = text("""
        INSERT INTO admins (admin_id, first_name, last_name, password_hash)
        VALUES (:admin_id, :first_name, :last_name, :password_hash)
    """)

    with app.app_context():
        for admin in admins:
            db.session.execute(insert_query, {
                "admin_id": admin["admin_id"],
                "first_name": admin["first_name"],
                "last_name": admin["last_name"],
                "password_hash": generate_password_hash(admin["password"])
            })
        db.session.commit()
        print("5 admins inserted successfully.")

if __name__ == "__main__":
    insert_admins()
