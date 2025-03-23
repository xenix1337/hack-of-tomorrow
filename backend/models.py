from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Player(Base):
    """
    Represents a player in the game.
    
    Attributes:
        id (int): The unique identifier for the player.
        bc_address (str): The blockchain address of the player.
        name (str): The name of the player.
        race (str): The race of the player (e.g., Human, Elf, etc.).
        level (int): The level of the player, which indicates their progress in the game.
    """
    __tablename__ = "players"
    id = Column(Integer, primary_key=True, index=True)
    bc_address = Column(String, index=True)
    name = Column(String, index=True)
    race = Column(String, index=True)
    level = Column(Integer, index=True)


class Location(Base):
    """
    Represents a location in the game world.
    
    Attributes:
        id (int): The unique identifier for the location.
        name (str): The name of the location.
    """
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)


class Quest(Base):
    """
    Represents a quest in the game.
    
    Attributes:
        id (int): The unique identifier for the quest.
        name (str): The name of the quest.
        description (str): A detailed description of the quest.
        reward (str): The reward given upon completing the quest.
    """
    __tablename__ = "quests"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    reward = Column(String, index=True)


class Agent(Base):
    """
    Represents an agent in the game, such as an NPC or a character providing quests.
    
    Attributes:
        id (int): The unique identifier for the agent.
        location_id (int): The foreign key linking the agent to a specific location.
        personality (str): A brief description of the agent's personality.
        background (str): A description of the agent's backstory or background.
        name (str): The name of the agent.
    """
    __tablename__ = "agents"
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), index=True)
    personality = Column(String, index=True)
    background = Column(String, index=True)
    name = Column(String, index=True)


class Event(Base):
    """
    Represents an event that occurs in the game, typically tied to a player.
    
    Attributes:
        id (int): The unique identifier for the event.
        player_id (int): The foreign key linking the event to a specific player.
        description (str): A description of the event.
    """
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), index=True)
    description = Column(String, index=True)


class Relationship(Base):
    """
    Represents a relationship between two agents in the game.
    
    Attributes:
        id (int): The unique identifier for the relationship.
        agent_source (int): The ID of the source agent in the relationship.
        agent_destination (int): The ID of the destination agent in the relationship.
        description (str): A description of the nature of the relationship.
    """
    __tablename__ = "relationships"
    id = Column(Integer, primary_key=True, index=True)
    agent_source = Column(Integer, index=True)
    agent_destination = Column(Integer, index=True)
    description = Column(String, index=True)
