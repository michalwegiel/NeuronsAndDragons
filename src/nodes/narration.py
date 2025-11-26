from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from rich.console import Console
from typing import Literal, Optional
from pydantic import BaseModel, Field

from core import GameState
from core.save import SaveManager
from nodes.lore_search import lore_assistant
from nodes.constants import MODEL_NAME
from nodes.utils import get_player_choice, list_available_player_choices

load_dotenv()

console = Console()


class SceneUpdate(BaseModel):
    narrative: str = Field(description="Story text to display to the player describing what happens next.")
    summary: str = Field(description="One line summary of scene narrative. Used for history aggregation.")
    user_options: list[str] = Field(
        description=(
            "List of possible actions the player can take next. "
            "Each option should be a short, self-contained string describing the action. "
            "Depending on situation, user should have at least 2 options and no more than 5."
        )
    )
    next_scene_type: list[Literal["narration", "exploration", "combat", "dialogue", "camp"]] = Field(
        description=(
            "A list of appropriate scene types that should occur based on player choice. "
            "Each user option should have corresponding outcome scene type. "
            "Used by the engine to branch the story."
        ),
    )
    location: Optional[str] = Field(
        default=None, description="If the player moves to a new location, specify the new location name."
    )


model = ChatOpenAI(model=MODEL_NAME, temperature=0.9).with_structured_output(SceneUpdate)


def narration(state: GameState) -> GameState:
    lore_assistant(state)
    state_str = state.model_dump_json()
    prompt = ChatPromptTemplate(
        [
            SystemMessage(
                "You are the Dungeon Master in a fantasy text RPG called 'Neurons & Dragons'.\n"
                "Generate the next scene based on the current game state below.\n"
                "Respond strictly following the SceneUpdate schema.\n"
                "RULES:\n"
                "- Always push the story forward. Avoid repeating similar actions or loops.\n"
                "- Avoid providing similar options or situations that are included in campaign history.\n"
                "- Avoid giving the same exploration choices repeatedly.\n"
                "- Provide meaningful narrative progression.\n"
                "- Create camp option if player has lower hp than 50.\n"
                "- user_options must be 2–5 items.\n"
                "- next_scene_type MUST have exactly the same length as user_options.\n"
                "- next_scene_type choices should vary depending on the action, not repeat.\n"
                "- If player is stuck, introduce a new development (NPC, danger, discovery).\n"
            ),
            HumanMessagePromptTemplate.from_template("Current game state:\n{state}"),
        ]
    )
    chain = prompt | model
    response: SceneUpdate = chain.invoke({"state": state_str})

    narrative = response.narrative
    summary = response.summary
    user_options = response.user_options
    next_scene_type = response.next_scene_type
    location = response.location

    console.print(f"\n{narrative}\n")
    state.history.append(f"dungeon master: {summary}")
    state.world.location = location if location is not None else state.world.location

    list_available_player_choices(choices=user_options)
    choice = get_player_choice("Your action", len(user_options))

    state.scene_type = next_scene_type[choice - 1]
    state.history.append(f"player action: {user_options[choice - 1]}")

    SaveManager().save(state)
    return state
