import ast
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.agents.agent_toolkits import create_retriever_tool


def initialize_llm() -> ChatOpenAI:
    """Initialize the LLM model."""
    return ChatOpenAI(model="gpt-4o-mini")


def create_faiss_vector_db(proper_nouns):
    """Create FAISS vector store from a list of proper nouns."""
    vector_db = FAISS.from_texts(proper_nouns, OpenAIEmbeddings())
    retriever = vector_db.as_retriever(search_kwargs={"k": 3})
    return retriever


def create_retriever_tool_with_description(retriever):
    """Create a retriever tool with a description for handling proper nouns."""
    description = """Use this tool to look up values to filter on. Input is an approximate spelling of the proper noun, 
    output is valid proper nouns. Use the noun most similar to the search."""

    retriever_tool = create_retriever_tool(
        retriever,
        name="search_proper_nouns",
        description=description,
    )

    return retriever_tool


def query_table_columns(db, table_name, columns):
    """Query specified columns from a given table and return a cleaned list of concatenated values."""
    try:
        # Dynamically build the SQL query for any table and columns
        column_str = ", ".join(columns)
        query = f"SELECT {column_str} FROM {table_name}"

        # Execute the query and fetch the results
        result = db.run(query)

        # Parse the result and concatenate column values into full names or concatenated strings
        cleaned_result = [
            " ".join(item.strip() for item in row if item)
            for row in ast.literal_eval(result)
        ]

        # Remove duplicates and return the final list
        return list(set(cleaned_result))
    except Exception as e:
        print(f"Error executing query for table {table_name}: {e}")
        return []


def get_proper_noun(db):
    actor_names = query_table_columns(db, "actor", ["first_name", "last_name"])
    city = query_table_columns(db, "city", ["city"])
    country = query_table_columns(db, "country", ["country"])

    # Combine data from multiple tables
    proper_nouns = actor_names + city + country

    return proper_nouns


def create_sql_agent(db, llm: ChatOpenAI, retriever_tool):
    """Create an SQL agent with a given database and LLM."""
    try:
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        tools = toolkit.get_tools()

        # Add retriever tool to the tools list
        tools.append(retriever_tool)

        SQL_PREFIX = """You are an agent designed to interact with a SQL database.
        Given an input question, create a syntactically correct PostgreSQL query to run, then look at the results of the query and return the answer.
        Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most 5 results.
        You can order the results by a relevant column to return the most interesting examples in the database.
        Never query for all the columns from a specific table, only ask for the relevant columns given the question.
        You have access to tools for interacting with the database.
        Only use the below tools. Only use the information returned by the below tools to construct your final answer.
        You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

        DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

        To start you should ALWAYS look at the tables in the database to see what you can query.
        Do NOT skip this step.
        Then you should query the schema of the most relevant tables."""

        # system_message = SystemMessage(content=SQL_PREFIX)

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SQL_PREFIX),
                ("placeholder", "{messages}"),
            ]
        )

        def _modify_state_messages(state: AgentState):
            return prompt.invoke({"messages": state["messages"]}).to_messages()

        # agent_executor = create_react_agent(llm, tools, state_modifier=system_message)

        agent_executor = create_react_agent(
            llm, tools, state_modifier=_modify_state_messages
        )

        return agent_executor
    except Exception as e:

        return None


def execute_agent_query(agent_executor, query: str) -> None:
    """Send a query to the agent executor and process the response."""
    try:
        messages = agent_executor.invoke({"messages": [("human", query)]})
        print(f"query : {query}")
        print(f"output : {messages["messages"][-1].content}")

    except Exception as e:
        print(e)
