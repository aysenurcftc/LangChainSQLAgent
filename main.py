from agent.agent import (
    initialize_llm,
    get_proper_nouns,
    create_faiss_vector_db,
    create_retriever_tool_with_description,
    create_sql_agent,
    execute_agent_query,
)
from db.db_module import connect_to_db, wrap_connection_to_sqldatabase
import streamlit as st

st.title("🤖 SQL Agent Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Maintain a single database connection in session state
if "db_connection" not in st.session_state:
    st.session_state.db_connection = connect_to_db()

# Maintain a wrapped database object
if "db" not in st.session_state:
    if st.session_state.db_connection:
        st.session_state.db = wrap_connection_to_sqldatabase(
            st.session_state.db_connection
        )
    else:
        st.error("Failed to connect to the database. Please try again.")

# Initialize FAISS vector store once
if "faiss_vector_db" not in st.session_state and "db" in st.session_state:
    db = st.session_state.db
    proper_nouns = get_proper_nouns(db)
    st.session_state.faiss_vector_db = create_faiss_vector_db(proper_nouns)

# Initialize LLM once
if "llm" not in st.session_state:
    st.session_state.llm = initialize_llm(
        st.session_state.get("openai_model", "gpt-3.5-turbo")
    )

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input for a query
if user_query := st.chat_input("Ask a question about the database:"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_query})

    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(user_query)

    # Process the user query using the SQL agent
    if "db" in st.session_state and st.session_state.db:
        try:
            db = st.session_state.db
            retriever = st.session_state.faiss_vector_db
            retriever_tool = create_retriever_tool_with_description(retriever)
            agent_executor = create_sql_agent(db, st.session_state.llm, retriever_tool)

            if agent_executor:
                # Display assistant response in chat message container
                with st.chat_message("assistant"):
                    response_placeholder = st.empty()

                    # Get the assistant's response (non-streaming)
                    response = execute_agent_query(agent_executor, user_query)

                    # Check if response is valid
                    if response:
                        response_text = response
                    else:
                        print(
                            "No response from the SQL agent. Please try rephrasing your question."
                        )

                    # Update the placeholder with the response text
                    response_placeholder.markdown(response_text)

                    # Add assistant's response to chat history
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response_text}
                    )
            else:
                st.error("Failed to create the SQL agent.")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            if "db_connection" in st.session_state and st.session_state.db_connection:
                st.session_state.db_connection.close()
