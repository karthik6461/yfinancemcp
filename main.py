from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent import FinancialAIAgent
import os

app = FastAPI()
agent = FinancialAIAgent(mcp_server_url=os.getenv("MCP_SERVER_URL", "http://localhost:8000"))

class QueryRequest(BaseModel):
    query: str

@app.post("/query")
async def process_query(request: QueryRequest):
    try:
        response = agent.process_query(request.query)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)