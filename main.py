from db_module import connect_to_db, wrap_connection_to_sqldatabase
from agent import (
    initialize_llm,
    create_sql_agent,
    execute_agent_query,
    create_faiss_vector_db,
    create_retriever_tool_with_description,
    query_table_columns,
)


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

            actor_names = query_table_columns(db, "actor", ["first_name", "last_name"])
            city = query_table_columns(db, "city", ["city"])
            country = query_table_columns(db, "country", ["country"])

            # Combine data from multiple tables
            proper_nouns = actor_names + city + country

            vector_db = create_faiss_vector_db(proper_nouns)

            retriever_tool = create_retriever_tool_with_description(vector_db)

            # result = retriever_tool.invoke("Ed Chase")
            # print(result)

            agent_executor = create_sql_agent(db, llm, retriever_tool)

            if agent_executor:
                execute_agent_query(
                    agent_executor,
                    "How many people named Ed Chase are there in the actor table?",
                )
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
