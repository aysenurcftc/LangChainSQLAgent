
# LangChain SQL Agent 


![agent_sql](https://github.com/aysenurcftc/LangChainSQLAgent/blob/main/sql_agent.png)

This project is a system that connects to a PostgreSQL database and runs AI-powered SQL queries. It uses LangChain and FAISS to convert database content into vector format and generate SQL queries based on natural language questions. This makes data retrieval from the database faster and more accurate. The project also features a user-friendly interface with Streamlit.

![agen](https://github.com/aysenurcftc/LangChainSQLAgent/blob/main/agent.png)


## Environment Variables


`OPENAI_API_KEY=`

`LANGCHAIN_API_KEY=`

`DB_USER=`

`DB_PASSWORD=`

`DB_HOST=`

`DB_PORT=`

`DB_NAME=`

## Run Locally

Clone the project

```bash
  https://github.com/aysenurcftc/LangChainSQLAgent.git
```

Go to the project directory

```bash
  cd LangChainSQLAgent
```

Install dependencies

```bash
    pipenv install
```

Start the project

```bash
   streamlit run python main.py

```


