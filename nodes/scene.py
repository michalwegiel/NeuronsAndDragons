import json

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from rich.console import Console
from typing import Literal
from pydantic import BaseModel, Field, TypeAdapter
from rich.prompt import Prompt

from core import GameState

load_dotenv()

console = Console()
model = ChatOpenAI(model="gpt-5-nano", temperature=0.9)


class SceneUpdate(BaseModel):
    narrative: str = Field(description="Story text to display to the player describing what happens next.")
    user_options: list[str] = Field(
        description=(
            "List of possible actions or dialogue choices the player can take next. "
            "Each option should be a short, self-contained string describing the action. "
            "Depending on situation, user should have at least 2 options and no more than 5."
        )
    )
    next_scene_type: list[Literal["exploration", "combat", "dialogue"]] = Field(
        description=(
            "A list of appropriate scene types that should occur based on player choice. "
            "Each user option should have corresponding outcome scene type. "
            "Used by the engine to branch the story."
        ),
    )
    location: str = Field(
        description="If the player moves to a new location, specify the new location name."
    )


scene_update_schema_json = json.dumps(TypeAdapter(SceneUpdate).json_schema(), indent=2)


def scene(state: GameState) -> GameState:
    state_str = json.dumps(state, indent=2, default=vars)
    prompt = (
        "You are the Dungeon Master in our fantasy text‐RPG 'Neurons & Dragons'.\n"
        f"Here is the current game state:\n{state_str}\n"
        f"Respond with valid JSON matching this schema:\n{scene_update_schema_json}"
    )

    resp = model.invoke(prompt)
    content = json.loads(resp.content)

    narrative = content["narrative"]
    user_options = content["user_options"]
    next_scene_type = content["next_scene_type"]
    location = content["location"]

    console.print("\n" + narrative)
    state.history.append(f'"dm": {narrative}')
    state.world.location = location

    console.print("\n")
    for i, option in enumerate(user_options, 1):
        console.print(f"{i}) {option}\n")

    choice = int(Prompt.ask("\nChoose your action").strip())
    state.scene_type = next_scene_type[choice - 1]
    state.history.append(f'"player_action": {user_options[choice - 1]}')

    return state
