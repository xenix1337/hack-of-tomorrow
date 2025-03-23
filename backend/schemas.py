from pydantic import BaseModel

class PlayerSchema(BaseModel):
    """
    Schema for Player data transfer object (DTO).
    
    Attributes:
        id (int): The unique identifier for the player.
        bc_address (str): The blockchain address of the player.
        name (str): The name of the player.
        race (str): The race of the player (e.g., Human, Elf, etc.).
        level (int): The level of the player, indicating their progress.
    
    Config:
        from_attributes (bool): Automatically populate attributes from database models.
    """
    id: int
    bc_address: str
    name: str
    race: str
    level: int

    class Config:
        from_attributes = True


class LocationSchema(BaseModel):
    """
    Schema for Location data transfer object (DTO).
    
    Attributes:
        id (int): The unique identifier for the location.
        name (str): The name of the location.
    
    Config:
        from_attributes (bool): Automatically populate attributes from database models.
    """
    id: int
    name: str

    class Config:
        from_attributes = True


class QuestSchema(BaseModel):
    """
    Schema for Quest data transfer object (DTO).
    
    Attributes:
        id (int): The unique identifier for the quest.
        name (str): The name of the quest.
        description (str): A description of the quest.
        reward (str): The reward provided upon completing the quest.
    
    Config:
        from_attributes (bool): Automatically populate attributes from database models.
    """
    id: int
    name: str
    description: str
    reward: str

    class Config:
        from_attributes = True


class AgentSchema(BaseModel):
    """
    Schema for Agent data transfer object (DTO).
    
    Attributes:
        id (int): The unique identifier for the agent.
        location_id (int): The foreign key linking the agent to a specific location.
        personality (str): A brief description of the agent's personality.
        background (str): A description of the agent's backstory or background.
        name (str): The name of the agent.
    
    Config:
        from_attributes (bool): Automatically populate attributes from database models.
    """
    id: int
    location_id: int
    personality: str
    background: str
    name: str

    class Config:
        from_attributes = True


class RelationshipSchema(BaseModel):
    """
    Schema for Relationship data transfer object (DTO).
    
    Attributes:
        id (int): The unique identifier for the relationship.
        agent_source (int): The ID of the source agent in the relationship.
        agent_destination (int): The ID of the destination agent in the relationship.
        description (str): A description of the nature of the relationship.
    
    Config:
        from_attributes (bool): Automatically populate attributes from database models.
    """
    id: int
    agent_source: int
    agent_destination: int
    description: str

    class Config:
        from_attributes = True


class EnterLocationSchema(BaseModel):
    """
    Schema for entering a location in the game.
    
    Attributes:
        location_id (int): The ID of the location the player is entering.
        player_id (int): The ID of the player entering the location.
    """
    location_id: int
    player_id: int


class SaySchema(BaseModel):
    """
    Schema for sending a message from a player to an agent.
    
    Attributes:
        player_id (int): The ID of the player sending the message.
        agent_id (int): The ID of the agent receiving the message.
        message (str): The content of the message being sent.
    """
    player_id: int
    agent_id: int
    message: str


class LeaveLocationSchema(BaseModel):
    """
    Schema for a player leaving a location.
    
    Attributes:
        player_id (int): The ID of the player leaving the location.
    """
    player_id: int


class RelationshipDescriptor(BaseModel):
    """
    Schema for describing a relationship between two characters.
    
    Attributes:
        destination_character_name (str): The name of the destination character.
        relation_description (str): A description of the nature of the relationship.
    """
    destination_character_name: str
    relation_description: str


class EventSchema(BaseModel):
    """
    Schema for Event data transfer object (DTO).
    
    Attributes:
        id (int): The unique identifier for the event.
        player_id (int): The ID of the player associated with the event.
        description (str): A description of the event.
    
    Config:
        from_attributes (bool): Automatically populate attributes from database models.
    """
    id: int
    player_id: int
    description: str

    class Config:
        from_attributes = True
