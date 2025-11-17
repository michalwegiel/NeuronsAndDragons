from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from rich.console import Console
from typing import Literal, Optional
from pydantic import BaseModel, Field

from core import GameState
from core.save import SaveManager
from nodes.utils import get_player_choice

load_dotenv()

console = Console()


class SceneUpdate(BaseModel):
    narrative: str = Field(description="Story text to display to the player describing what happens next.")
    summary: str = Field(description="One line summary of scene narrative. Used for history aggregation.")
    user_options: list[str] = Field(
        description=(
            "List of possible actions or dialogue choices the player can take next. "
            "Each option should be a short, self-contained string describing the action. "
            "Depending on situation, user should have at least 2 options and no more than 5."
        )
    )
    next_scene_type: list[Literal["narration", "exploration", "combat", "dialogue"]] = Field(
        description=(
            "A list of appropriate scene types that should occur based on player choice. "
            "Each user option should have corresponding outcome scene type. "
            "Used by the engine to branch the story."
        ),
    )
    location: Optional[str] = Field(
        default=None,
        description="If the player moves to a new location, specify the new location name."
    )


model = ChatOpenAI(model="gpt-5-nano", temperature=0.9).with_structured_output(SceneUpdate)


def narration(state: GameState) -> GameState:
    state_str = state.model_dump_json()
    prompt = (
        "You are the Dungeon Master in a fantasy text RPG called 'Neurons & Dragons'.\n"
        "Generate the next scene based on the current game state below.\n"
        "Respond strictly following the SceneUpdate schema.\n"
        "RULES:\n"
        "- Always push the story forward. Avoid repeating similar actions or loops.\n"
        "- Avoid giving the same exploration choices repeatedly.\n"
        "- Provide meaningful narrative progression.\n"
        "- user_options must be 2–5 items.\n"
        "- next_scene_type MUST have exactly the same length as user_options.\n"
        "- next_scene_type choices should vary depending on the action, not repeat.\n"
        "- If player is stuck, introduce a new development (NPC, danger, discovery).\n\n"
        f"Current game state:\n{state_str}\n"
    )

    response: SceneUpdate = model.invoke(prompt)

    narrative = response.narrative
    summary = response.summary
    user_options = response.user_options
    next_scene_type = response.next_scene_type
    location = response.location

    console.print(f"\n{narrative}\n")
    state.history.append(f'dungeon master: {summary}')
    state.world.location = location if location is not None else state.world.location

    for i, option in enumerate(user_options, 1):
        console.print(f"{i}) {option}")
    console.print("")

    choice = get_player_choice("Your action", len(user_options))

    state.scene_type = next_scene_type[choice - 1]
    state.history.append(f'player action: {user_options[choice - 1]}')

    SaveManager().save(state)
    return state
