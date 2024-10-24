from db_module import connect_to_db, wrap_connection_to_sqldatabase
from agent import initialize_llm, create_sql_agent, execute_agent_query

def main():
    """Main entry point for the application."""
    conn = None
    try:
        conn = connect_to_db()
        if conn is None:
            print("Failed to connect to the database. Exiting.")
            return

        with conn:
            db = wrap_connection_to_sqldatabase()
            if db is None:
                print("Failed to wrap the database connection. Exiting.")
                return

            llm = initialize_llm()
            agent_executor = create_sql_agent(db, llm)

            if agent_executor:
                execute_agent_query(agent_executor, "How many customers are there?")
            else:
                print("Failed to create the SQL agent. Exiting.")
                return

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed")



if __name__ == "__main__":
    main()
