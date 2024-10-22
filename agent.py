from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.prebuilt import create_react_agent



def initialize_llm() -> ChatOpenAI:
    """Initialize the LLM model."""
    return ChatOpenAI(model="gpt-3.5-turbo")

def create_sql_agent(db, llm: ChatOpenAI):
    """Create an SQL agent with a given database and LLM."""
    try:
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        tools = toolkit.get_tools()

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

        system_message = SystemMessage(content=SQL_PREFIX)
        agent_executor = create_react_agent(llm, tools, state_modifier=system_message)

        return agent_executor
    except Exception as e:

        return None

def execute_agent_query(agent_executor, query: str) -> None:
    """Send a query to the agent executor and process the response."""
    try:
        for response in agent_executor.stream({"messages": [HumanMessage(content=query)]}):
            print(response)
            print("----")
    except Exception as e:
        print(e)


