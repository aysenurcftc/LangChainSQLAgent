import os
import ast
import psycopg2
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase

load_dotenv()


def connect_to_db():
    """Establish connection to the PostgreSQL database using environment variables."""
    try:
        conn = psycopg2.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
        )
        print("Database connection established.")
        return conn
    except psycopg2.DatabaseError as e:
        print(f"Database connection failed: {e}")
        return None


def wrap_connection_to_sqldatabase(conn):
    """Wrap the PostgreSQL connection in a LangChain SQLDatabase object."""
    try:
        db_uri = (
            f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
            f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        )
        return SQLDatabase.from_uri(db_uri)
    except Exception as e:
        print(f"Error wrapping database connection: {e}")
        return None


def query_table_columns(db, table_name: str, columns: list) -> list:
    """Query specified columns from a given table and return a cleaned list of concatenated values."""
    try:
        column_str = ", ".join(columns)
        query = f"SELECT {column_str} FROM {table_name}"
        result = db.run(query)
        cleaned_result = [
            " ".join(item.strip() for item in row if item)
            for row in ast.literal_eval(result)
        ]
        return list(set(cleaned_result))
    except Exception as e:
        print(f"Error querying {table_name}: {e}")
        return []
