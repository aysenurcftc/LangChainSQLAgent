import os
import ast
import re
import psycopg2
from psycopg2 import DatabaseError
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
        return conn
    except DatabaseError as e:
        print(f"Database connection failed: {e}")
        return None


def wrap_connection_to_sqldatabase():
    """Wrap the PostgreSQL connection in a LangChain SQLDatabase object using environment variables."""
    try:
        db_uri = (
            f"postgresql://{os.getenv('DB_USER')}:"
            f"{os.getenv('DB_PASSWORD')}@"
            f"{os.getenv('DB_HOST')}:"
            f"{os.getenv('DB_PORT')}/"
            f"{os.getenv('DB_NAME')}"
        )
        db = SQLDatabase.from_uri(db_uri)
        return db
    except Exception as e:
        print(f"Error wrapping the database connection: {e}")
        return None


def query_as_list(db, query):
    res = db.run(query)
    res = [el for sub in ast.literal_eval(res) for el in sub if el]
    res = [re.sub(r"\b\d+\b", "", string).strip() for string in res]
    return list(set(res))
