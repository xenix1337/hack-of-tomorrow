import asyncio
import json
import logging
import os
from asyncio import gather
from datetime import datetime
from typing import Dict, List, Any

import httpx
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from uagents import Agent, Context, Model
from uagents.envelope import Envelope
from uagents.query import query

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app initialization
app = FastAPI()

# Enviroment variables
token = os.getenv("LLM_API_TOKEN")
llm_api_url = os.getenv("LLM_URL")
llm_model = os.getenv("LLM_MODEL")

if not all([token, llm_api_url, llm_model]):
    raise RuntimeError(
        "Missing required environment variables: LLM_API_TOKEN, LLM_URL, LLM_MODEL"
    )

agents: Dict[str, Agent] = {}
initial_contexts: Dict[str, str] = {}


class AgentMessage(Model):
    message: str


class SendMessageRequest(BaseModel):
    sender: str
    recipients: List[str]
    message: str


class AgentResponse(Model):
    text: str


class AgentConfiguration(BaseModel):
    name: str
    port: int
    seed: str
    endpoint: str | list[str]


class InitialContextRequest(BaseModel):
    agent_address: str
    initial_context: str


class InitialContextResponse(BaseModel):
    status: str
    message: str


@app.post("/init")
async def set_initial_context(request: InitialContextRequest) -> InitialContextResponse:
    """Sets the initial context for a given agent."""
    initial_contexts[request.agent_address] = request.initial_context
    logger.info(f"Initial context set for {request.agent_address}")
    return InitialContextResponse(
        status="success", message=f"Initial context set for {request.agent_address}"
    )


@app.post("/send-message")
async def process_message(request: SendMessageRequest) -> Any:
    """Processes and sends a message to multiple agents."""
    logger.info(f"Processing message from {request.sender} to {request.recipients}")

    query_tasks = []
    for recipient in request.recipients:
        initial_context = initial_contexts.get(recipient, "")
        combined_message = (
            f"{initial_context}\n{request.message}"
            if initial_context
            else request.message
        )
        query_tasks.append(
            agent_query(recipient, AgentMessage(message=combined_message))
        )

    responses = await gather(*query_tasks)
    results = dict(zip(request.recipients, responses))
    return {"status": "completed", "results": results}


async def agent_query(destination: str, req: AgentMessage) -> Any:
    """Queries an agent with a given message."""
    response = await query(destination=destination, message=req, timeout=15)
    if isinstance(response, Envelope):
        return json.loads(response.decode_payload())
    return response


def create_agent(config: AgentConfiguration) -> Agent:
    """Creates an agent with the given configuration."""
    agent = Agent(
        name=config.name, port=config.port, seed=config.seed, endpoint=config.endpoint
    )

    @agent.on_query(model=AgentMessage, replies={AgentResponse})
    async def query_handler(ctx: Context, sender: str, msg: AgentMessage):
        logger.info(f"[{config.name}] Received message at {datetime.now()}")

        llm_response = await fetch_llm_response(msg.message)
        await ctx.send(sender, AgentResponse(text=llm_response))

    return agent


async def fetch_llm_response(message: str) -> str:
    """Fetches a response from the LLM API."""
    payload = {
        "model": llm_model,
        "messages": [{"role": "user", "content": message}],
        "temperature": 0.7,
        "stream": False,
        "max_tokens": 1000,
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                llm_api_url, headers=headers, json=payload, timeout=15
            )
            response.raise_for_status()
            data = response.json()
            return (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "No response")
            )
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP {e.response.status_code} error querying LLM: {e}")
    except Exception as e:
        logger.error(f"Unexpected error querying LLM: {e}")
    return "Error: Unable to fetch response from LLM"


async def start_agents() -> None:
    """Starts all agents based on configuration."""
    with open("agents.json") as f:
        agent_configs = [AgentConfiguration(**config) for config in json.load(f)]

    for config in agent_configs:
        agents[config.name] = create_agent(config)

    await gather(*(agent.run_async() for agent in agents.values()))


async def main() -> None:
    """Runs the FastAPI server and agents concurrently."""
    agent_task = asyncio.create_task(start_agents())
    server = uvicorn.Server(uvicorn.Config(app, host="0.0.0.0", port=9080))
    server_task = asyncio.create_task(server.serve())

    await gather(agent_task, server_task)


if __name__ == "__main__":
    asyncio.run(main())
