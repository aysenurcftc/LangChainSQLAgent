
# LangChain SQL Agent 

This project is a system that connects to a PostgreSQL database and executes AI-powered SQL queries. Using LangChain and FAISS, it processes database content in vector format and generates SQL queries that respond to questions asked in natural language. This optimizes database data retrieval and provides accurate results to the user.



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
   pipenv run python main.py

```

