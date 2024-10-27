from langchain_core.prompts import ChatPromptTemplate
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.prebuilt import create_react_agent
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.agents.agent_toolkits import create_retriever_tool
from db.db_module import query_table_columns


def initialize_llm(model_name="gpt-3.5-turbo") -> ChatOpenAI:
    """Initialize the LLM model."""
    return ChatOpenAI(model=model_name)


def create_faiss_vector_db(proper_nouns: list) -> VectorStoreRetriever:
    """Create a FAISS vector store from a list of proper nouns."""
    vector_db = FAISS.from_texts(proper_nouns, OpenAIEmbeddings())
    return vector_db.as_retriever(search_kwargs={"k": 3})


def create_retriever_tool_with_description(retriever):
    """Create a retriever tool with a description for handling proper nouns."""
    description = (
        "Use this tool to look up values to filter on. Input is an approximate spelling of "
        "the proper noun, output is valid proper nouns. Use the noun most similar to the search."
    )
    return create_retriever_tool(
        retriever, name="search_proper_nouns", description=description
    )


def get_proper_nouns(db):
    """Retrieve proper nouns from the specified tables."""
    actor_names = query_table_columns(db, "actor", ["first_name", "last_name"])
    cities = query_table_columns(db, "city", ["city"])
    countries = query_table_columns(db, "country", ["country"])
    return actor_names + cities + countries


def create_sql_agent(db, llm: ChatOpenAI, retriever_tool):
    """Create an SQL agent with a given database and LLM."""
    try:
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        tools = toolkit.get_tools() + [retriever_tool]
        sql_prefix = (
            "You are an agent designed to interact with a SQL database. Given an input question, create a "
            "syntactically correct PostgreSQL query to run, then look at the results of the query and return the answer. "
            "Always double-check your query before execution and limit the results to at most 5 unless specified."
        )
        prompt = ChatPromptTemplate.from_messages(
            [("system", sql_prefix), ("placeholder", "{messages}")]
        )
        agent_executor = create_react_agent(
            llm,
            tools,
            state_modifier=lambda state: prompt.invoke(
                {"messages": state["messages"]}
            ).to_messages(),
        )
        return agent_executor
    except Exception as e:
        print(f"Failed to create SQL agent: {e}")
        return None


def execute_agent_query(agent_executor, query: str):
    """Send a query to the agent executor and process the response."""
    try:
        messages = agent_executor.invoke({"messages": [("human", query)]})
        # print(f"Query: {query}")
        # print(f"Output: {messages['messages'][-1].content}")
        return messages["messages"][-1].content
    except Exception as e:
        print(f"Error executing query: {e}")
