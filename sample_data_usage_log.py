import csv  # For reading CSV files
from app import app, db  # Flask app and SQLAlchemy instance
from werkzeug.security import generate_password_hash  # For hashing passwords
from sqlalchemy import text  # Required to safely wrap raw SQL queries

# Function to import students from a CSV into the PostgreSQL database
def import_students(csv_file_path):
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)

        # Wrap your raw SQL insert query with SQLAlchemy's text() function
        insert_query = text("""
        INSERT INTO students (student_id, first_name, last_name, password_hash)
        VALUES (:student_id, :first_name, :last_name, :password_hash)
        """)

        inserted_count = 0

        with app.app_context():
            for row in reader:
                # Hash the password before inserting into the DB
                hashed_password = generate_password_hash(row['password_hash'])

                # Execute the insert query using parameters
                db.session.execute(insert_query, {
                    'student_id': row['student_id'],
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                    'password_hash': hashed_password
                })

                inserted_count += 1  # Increment counter

            db.session.commit()  # Save all inserts to the database
            print(f"{inserted_count} students imported successfully.")

# Run the function only if this file is executed directly
if __name__ == "__main__":
    import_students("./utils/students_data.csv")  # Make sure path is correct
