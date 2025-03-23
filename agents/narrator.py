import os
import json
import logging
import datetime
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Union
import uvicorn

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
token = os.getenv("LLM_API_TOKEN")
llm_api_url = os.getenv("LLM_URL")
llm_model = os.getenv("LLM_MODEL")

if not all([token, llm_api_url, llm_model]):
    raise RuntimeError(
        "Missing required environment variables: LLM_API_TOKEN, LLM_URL, LLM_MODEL"
    )

# Load agent configurations
with open("agents.json") as f:
    agents: List[str] = [agent["recipient_address"] for agent in json.load(f)]

# Global state
player_data: Dict[int, "PlayerSession"] = {}
agent_url_to_name: Dict[str, str] = {}
agent_name_to_id: Dict[str, int] = {}

# FastAPI app instance
app = FastAPI()


class CharacterInitializeRequest(BaseModel):
    agent_id: int
    name: str
    init_prompt: str


class InitializeRequest(BaseModel):
    player_id: int
    narrator_prompt: str
    characters: List[CharacterInitializeRequest]


class ActionRequest(BaseModel):
    player_id: int
    player_action: str


class ActionResponse(BaseModel):
    agent_id: int
    message: str


class PlayerSession:
    def __init__(
        self,
        player_id: int,
        narrator_prompt: str,
        characters: List[CharacterInitializeRequest],
    ):
        self.player_id = player_id
        self.narrator_prompt = narrator_prompt
        self.characters = characters
        self.current_dialogue: List[str] = []


@app.post("/initialize")
def initialize(request: InitializeRequest):
    """Initializes a player session with characters and a narrator prompt."""
    player_data[request.player_id] = PlayerSession(
        request.player_id, request.narrator_prompt, request.characters
    )

    if len(request.characters) != len(agents):
        raise HTTPException(
            status_code=400, detail="Mismatch between agents and characters"
        )

    for agent_url, character in zip(agents, request.characters):
        initialize_agent(request.player_id, agent_url, character)
        agent_url_to_name[agent_url] = character.name
        agent_name_to_id[character.name] = character.agent_id


@app.post("/action")
def process_action(request: ActionRequest) -> ActionResponse:
    """Processes a player action and retrieves the next response."""
    session = player_data.get(request.player_id)
    if not session:
        raise HTTPException(status_code=404, detail="Player session not found")

    session.current_dialogue.append(request.player_action)
    return send_message(request.player_id)


def initialize_agent(
    player_id: int, agent_url: str, character: CharacterInitializeRequest
):
    """Sends initialization request to an agent."""
    url = "http://127.0.0.1:9080/init"
    payload = {
        "player_id": player_id,
        "agent_address": agent_url,
        "initial_context": character.init_prompt,
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        logging.error(f"Failed to initialize agent {character.name} at {agent_url}")
        raise HTTPException(status_code=500, detail="Failed to initialize agent")


def eval_function(player_id: int, results: Dict[str, str]) -> ActionResponse:
    """Evaluates agent responses using the LLM model."""
    actions_str = [
        f"{agent_url_to_name[recipient]}: {message}"
        for recipient, message in results.items()
        if message != "silence"
    ]

    if not actions_str:
        return ActionResponse(
            agent_id=-1, message="*The room became filled with silence*"
        )

    session = player_data[player_id]
    prompt = session.narrator_prompt.replace(
        "{action_history}", "\n".join(session.current_dialogue)
    )
    prompt = prompt.replace("{agent_responses}", "\n".join(actions_str))

    payload = json.dumps(
        {
            "model": llm_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "stream": False,
            "max_tokens": 8000,
        }
    )
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    try:
        response = requests.post(llm_api_url, headers=headers, data=payload)
        response.raise_for_status()
        llm_response = response.json()
        llm_content = (
            llm_response.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "No response")
        )

        for recipient, message in results.items():
            if agent_url_to_name.get(recipient) in llm_content:
                logging.info(f"LLM chose: {agent_url_to_name[recipient]}")
                session.current_dialogue.append(
                    f"{agent_url_to_name[recipient]}: {message}"
                )
                return ActionResponse(
                    agent_id=agent_name_to_id[agent_url_to_name[recipient]],
                    message=message,
                )
    except requests.exceptions.RequestException as e:
        logging.error(f"HTTP error querying LLM: {e}")
    except Exception as e:
        logging.error(f"Unexpected error querying LLM: {e}")

    logging.warning("LLM evaluation failed or gave an incorrect answer")
    # If narrator LLM fails, return the first non-silence response.
    # This is still better than failing, and characters are ordered by priority by design.
    for recipient, message in results.items():
        return ActionResponse(
            agent_id=agent_name_to_id.get(agent_url_to_name.get(recipient), -1),
            message=message,
        )

    raise HTTPException(status_code=500, detail="No valid response found")


def send_message(player_id: int) -> ActionResponse:
    """Sends the player's current dialogue to agents and evaluates the response."""
    url = "http://127.0.0.1:9080/send-message"
    session = player_data.get(player_id)

    if not session:
        raise HTTPException(status_code=404, detail="Player session not found")

    payload = {
        "sender": "narrator",
        "recipients": agents,
        "message": "\n".join(session.current_dialogue),
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=payload)

    logging.info("Received response from agents")

    if response.status_code == 200:
        results = {
            k: v.get("text", "") for k, v in response.json().get("results", {}).items()
        }
        return eval_function(player_id, results)
    else:
        raise HTTPException(status_code=500, detail=f"Error: {response.text}")


if __name__ == "__main__":
    uvicorn.run("narrator:app", port=7999, reload=True)
