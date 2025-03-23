import uvicorn
from typing import List
from fastapi import HTTPException
from fastapi import status, FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, scoped_session

import models
from http_client import HttpClient
from lib.prompt_util import (
    generate_agent_initialization_prompt,
    generate_narrator_prompt,
)
from models import Player, Location, Quest, Agent, Relationship, Event
from schemas import *
from blockchain import (
    blockchain_create_player,
    blockchain_give_item,
    blockchain_get_player_data,
    blockchain_get_player_items,
)
from game_settings import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

app = FastAPI()


def get_db():
    """
    Dependency function to get the database session.

    @returns: Yields the database session.
    @rtype: Session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def startup():
    """
    FastAPI event handler to initialize the database.

    @returns: None
    @rtype: None
    """
    print("Debug: Models loaded in Base.metadata.tables:")
    print(models.Base.metadata.tables.keys())  # Check if models are registered
    models.Base.metadata.create_all(bind=engine)


httpClient = HttpClient(base_url=settings.API_BASE_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    """
    Root endpoint for the FastAPI RPG API.

    @returns: A welcome message.
    @rtype: dict
    """
    return {"message": "Welcome to the FastAPI RPG API!"}


@app.get("/players", response_model=List[PlayerSchema])
def get_players(db: Session = Depends(get_db)):
    """
    Retrieve all players from the database.

    @returns: A list of players.
    @rtype: List[PlayerSchema]
    """
    return db.query(Player).all()


@app.post("/players", response_model=PlayerSchema)
def create_player(player: PlayerSchema, db: Session = Depends(get_db)):
    """
    Create a new player in the database.

    @param player: The player data.
    @type player: PlayerSchema

    @returns: The created player.
    @rtype: PlayerSchema
    """
    try:
        with db.begin():
            db_player = Player(**player.dict())
            db.add(db_player)
            db.commit()
            db.refresh(db_player)

            blockchain_create_player(db_player.bc_address, 100)
            blockchain_give_item(db_player.bc_address, "bow")
            blockchain_give_item(db_player.bc_address, "health potion")

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error during blockchain operation: {str(e)}")
    
    return db_player

@app.get("/locations", response_model=List[LocationSchema])
def get_locations(db: Session = Depends(get_db)):
    """
    Retrieve all locations from the database.

    @returns: A list of locations.
    @rtype: List[LocationSchema]
    """
    return db.query(Location).all()


@app.post("/locations", response_model=LocationSchema)
def create_location(location: LocationSchema, db: Session = Depends(get_db)):
    """
    Create a new location in the database.

    @param location: The location data.
    @type location: LocationSchema

    @returns: The created location.
    @rtype: LocationSchema
    """
    db_location = Location(**location.dict())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location


@app.get("/quests", response_model=List[QuestSchema])
def get_quests(db: Session = Depends(get_db)):
    """
    Retrieve all quests from the database.


    @returns: A list of quests.
    @rtype: List[QuestSchema]
    """
    return db.query(Quest).all()


@app.post("/quests", response_model=QuestSchema)
def create_quest(quest: QuestSchema, db: Session = Depends(get_db)):
    """
    Create a new quest in the database.

    @param quest: The quest data.
    @type quest: QuestSchema

    @returns: The created quest.
    @rtype: QuestSchema
    """
    db_quest = Quest(**quest.dict())
    db.add(db_quest)
    db.commit()
    db.refresh(db_quest)
    return db_quest


@app.get("/agents", response_model=List[AgentSchema])
def get_agents(db: Session = Depends(get_db)):
    """
    Retrieve all agents from the database.


    @returns: A list of agents.
    @rtype: List[AgentSchema]
    """
    return db.query(Agent).all()


@app.post("/agents", response_model=AgentSchema)
def create_agent(agent: AgentSchema, db: Session = Depends(get_db)):
    """
    Create a new agent in the database.

    @param agent: The agent data.
    @type agent: AgentSchema

    @returns: The created agent.
    @rtype: AgentSchema
    """
    db_agent = Agent(**agent.dict())
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent


@app.get("/relationships", response_model=List[RelationshipSchema])
def get_relationships(db: Session = Depends(get_db)):
    """
    Retrieve all relationships between agents from the database.

    @returns: A list of relationships.
    @rtype: List[RelationshipSchema]
    """
    return db.query(Relationship).all()


@app.post("/relationships", response_model=RelationshipSchema)
def create_relationship(
    relationship: RelationshipSchema, db: Session = Depends(get_db)
):
    """
    Create a new relationship between agents in the database.

    @param relationship: The relationship data.
    @type relationship: RelationshipSchema

    @returns: The created relationship.
    @rtype: RelationshipSchema
    """
    db_relationship = Relationship(**relationship.dict())
    db.add(db_relationship)
    db.commit()
    db.refresh(db_relationship)
    return db_relationship


@app.post("/enterLocation", status_code=status.HTTP_200_OK)
async def enter_location(model: EnterLocationSchema, db: Session = Depends(get_db)):
    """
    Handle player entering a location.

    @param model: The location entry data.
    @type model: EnterLocationSchema

    @returns: A list of agent IDs present in the location.
    @rtype: dict
    """
    location = db.query(Location).filter(Location.id == model.location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    location_schema = LocationSchema.from_orm(location)  # Convert to Schema

    player = db.query(Player).filter(Player.id == model.player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    player_schema = PlayerSchema.from_orm(player)  # Convert to Schema

    player_events = db.query(Event).filter(Event.player_id == model.player_id).all()
    event_schemas = [EventSchema.from_orm(event) for event in player_events]

    agents = db.query(Agent).filter(Agent.location_id == model.location_id).all()
    agent_schemas = [AgentSchema.from_orm(agent) for agent in agents]
    agent_descriptions = []
    agent_prompts = []
    for agent in agent_schemas:
        agent_relationships = (
            db.query(Relationship).filter(Relationship.agent_source == agent.id).all()
        )
        relationship_schemas = [
            RelationshipSchema.from_orm(r) for r in agent_relationships
        ]
        relations: List[RelationshipDescriptor] = []
        for r in relationship_schemas:
            schema = next((s for s in agent_schemas if s.id == r.agent_destination), None)
            
            if schema is None:
                raise ValueError(f"agent_destination {r.agent_destination} not found in agent_schemas")
            
            relations.append(
                RelationshipDescriptor(
                    destination_character_name=schema.name,
                    relation_description=r.description,
                )
            )

        agent_prompt = generate_agent_initialization_prompt(
            location_schema, agent, relations, player_schema, event_schemas
        )
        agent_prompts.append(agent_prompt)
        agent_descriptions.append(
            f"{agent.name};{agent.personality};{agent.background}"
        )
    try:
        await httpClient.post(
            "/initialize",
            json={
                "player_id": 0,
                "narrator_prompt": generate_narrator_prompt(
                    location_name=location_schema.name,
                    nearby_npcs=agent_descriptions,
                    character_description=player_schema,
                ),
                "characters": [
                    {
                        "agent_id": agent_schema.id,
                        "name": agent_schema.name,
                        "init_prompt": agent_prompt,
                    }
                    for agent_schema, agent_prompt in zip(agent_schemas, agent_prompts)
                ],
            },
        )
    except:
        raise HTTPException(status_code=500, detail=f"Error with external API: {str(e)}")

    return {"agents_ids": [ag.id for ag in agent_schemas]}


@app.post("/say", status_code=status.HTTP_200_OK)
async def say(model: SaySchema, db: Session = Depends(get_db)):
    """
    Handle player interaction with an agent (say a message).

    @param model: The message data between the player and the agent.
    @type model: SaySchema

    @returns: The agent's response message.
    @rtype: dict
    """
    agent = db.query(Agent).filter(Agent.id == model.agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    player = db.query(Player).filter(Player.id == model.player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    agent_schema = AgentSchema.from_orm(agent)  # Convert to Schema
    response = await httpClient.post(
        "/action",
        json={
            "player_id": model.player_id,
            "player_action": f"Player says to {agent_schema.name}: {model.message}",
        },
    )

    return {
        "responder_id": response["agent_id"],
        "message": response["message"],
    }


@app.post("/leaveLocation", status_code=status.HTTP_200_OK)
def leave_location(model: LeaveLocationSchema):
    """
    Handle player leaving a location.

    @param model: The player data.
    @type model: LeaveLocationSchema

    @returns: A message indicating the player has left.
    @rtype: dict
    """
    return {"message": f"Player {model.player_id} left location"}


@app.get("/getPlayerData", status_code=status.HTTP_200_OK)
def get_player_data(id: int, db: Session = Depends(get_db)):
    """
    Retrieve player data from both the database and blockchain.

    @param id: The player ID.
    @type id: int

    @returns: The player data from the database and blockchain.
    @rtype: dict
    """
    db_player = db.query(Player).filter(Player.id == id).first()
    playerData = blockchain_get_player_data(db_player.bc_address)
    return {"db": db_player, "bc": {"money": playerData[0], "items": playerData[1]}}


@app.get("/getPlayerItems", status_code=status.HTTP_200_OK)
def get_player_items(id: int, db: Session = Depends(get_db)):
    """
    Retrieve the items owned by a player from the blockchain.

    @param id: The player ID.
    @type id: int

    @returns: A list of the player's items.
    @rtype: list
    """
    db_player = db.query(Player).filter(Player.id == id).first()
    return [
        {"id": item[0], "data": item[1]}
        for item in blockchain_get_player_items(db_player.bc_address)
    ]


@app.get("/events", response_model=List[EventSchema])
def get_events(db: Session = Depends(get_db)):
    """
    Retrieve all events from the database.

    @returns: A list of events.
    @rtype: List[EventSchema]
    """
    return db.query(Event).all()


@app.post("/events", response_model=EventSchema)
def create_event(event: EventSchema, db: Session = Depends(get_db)):
    """
    Create a new event in the database.

    @param event: The event data.
    @type event: EventSchema

    @returns: The created event.
    @rtype: EventSchema
    """
    db_event = Event(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
