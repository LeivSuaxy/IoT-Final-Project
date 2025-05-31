from core.database import create_db_and_tables
from core.models import * # Don't remove, necessary for migrations

if __name__ == '__main__':
    create_db_and_tables()
    print("Database and tables created successfully.")