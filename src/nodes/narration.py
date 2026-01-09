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
    narrative: str = Field(
        description=(
            "Detailed story text shown to the player describing what happens next in the scene. "
            "Write in present or past tense, immersive and descriptive."
        )
    )
    summary: str = Field(
        description=(
            "A single concise sentence summarizing the scene outcome. "
            "Used for history aggregation and logs. Do not include dialogue."
        )
    )
    user_options: list[str] = Field(
        description=(
            "List of actions the player can choose from next. "
            "Each option must be a short, self-contained sentence describing a single action. "
            "Provide between 2 and 5 options."
        )
    )
    next_scene_type: list[Literal["narration", "exploration", "combat", "dialogue", "camp"]] = Field(
        description=(
            "Scene type that results from choosing each user option. "
            "This list must have the same length and order as user_options. "
            "Used by the engine to branch the story."
        )
    )
    location: Optional[str] = Field(
        default=None, description="If the player moves to a new location, specify the new location name."
    )
    weather: Optional[str] = Field(default=None, description="If weather changes, specify a new weather.")
    quest: Optional[str] = Field(default=None, description="If quest changes, specify a new quest.")


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
    weather = response.weather
    quest = response.quest

    console.print(f"\n{narrative}\n")
    state.append_history(f"dungeon master: {summary}")
    state.world.location = location if location is not None else state.world.location
    state.world.weather = weather if weather is not None else state.world.weather
    state.world.quest = quest if quest is not None else state.world.quest

    list_available_player_choices(choices=user_options)
    choice = get_player_choice("Your action", len(user_options))

    state.scene_type = next_scene_type[choice - 1]
    state.append_history(f"player action: {user_options[choice - 1]}")

    SaveManager().save(state)
    return state
