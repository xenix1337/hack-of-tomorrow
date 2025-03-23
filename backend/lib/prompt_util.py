from string import Template
from models import *
from schemas import *
from blockchain import blockchain_get_player_items
from typing import List


def generate_agent_initialization_prompt(
    location: LocationSchema,
    agent: AgentSchema,
    relationships: List[RelationshipDescriptor],
    player: PlayerSchema,
    events: List[EventSchema],
) -> str:
    # Build relationships string
    relationships_text = "\n".join(
        f"With person <{r.destination_character_name}> your relation is <{r.relation_description}>"
        for r in relationships
    )
    
    # Generate player items and actions
    player_items = "\n".join(item[1] for item in blockchain_get_player_items(player.bc_address)) or "No items available"
    player_actions = "\n".join(event.description for event in events) or "No actions available"
    
    # Prepare prompt using Template
    prompt_template = Template("""
You are an interactive NPC in a video game. This is the personality of your character:
$personality

You are in:
$location_name.
Your role here is:
$background.
In this location, there are also other people.
$relationships_text

You are given a list of possible actions. Please choose **ONLY** one of them, and write it in a separate line.
Output **ONLY** this command and no other text. If you refuse to answer for some reason, just use the command `silence`.
Commands will have parameters marked by `[parameter]`. If you want to refer to the main player, use `Player` as their name.
Action list:
- `silence` - stay silent. No other commands can be used along this one.
- `[text]` - say [text] loud. All nearby NPCs will hear you.

Player enters your location. Their race is $race, their level is $level.
They are known for their recent and/or important actions/features:
$player_actions

They have the following items:
$player_items

Please write what you want to do using one or more commands.""")

    # Substitute variables into the template
    prompt = prompt_template.substitute(
        personality=agent.personality,
        location_name=location.name,
        background=agent.background,
        relationships_text=relationships_text.strip(),
        race=player.race,
        level=player.level,
        player_actions=player_actions,
        player_items=player_items
    )

    return prompt


def generate_narrator_prompt(
    location_name: str, nearby_npcs: List[str], character_description: str
) -> str:
    npcs = "\n".join(nearby_npcs) or ""
    prompt_template = Template("""
You are a storyteller in a role-playing game. The player is in $location_name. There are multiple NPC characters here, beside Player.
Here is a list of them in the format `Name; Personality; Background`:
$nearby_npcs

This is the description of the Player character:
$character_description

After a short action:
$action_history

[END OF CURRENT STORY]

Now, all NPCs have a desire to do their action! Your task is to choose one NPC whose action will be performed in the game.
Pick the best fitting one, most interesting, and making enjoyable and balanced gameplay. Not making the game too easy or too hard for the Player is your duty!

List of NPCs and actions they want to take:
$agent_responses

Pick only one by writing his name, and **ONLY** his name.""")

    # Substitute variables into the template
    prompt = prompt_template.substitute(
        location_name=location_name,
        nearby_npcs= npcs,
        character_description=character_description,
        action_history='{action_history}',  # Placeholder for dynamic action history
        agent_responses='{agent_responses}'  # Placeholder for dynamic agent responses
    )

    return prompt
