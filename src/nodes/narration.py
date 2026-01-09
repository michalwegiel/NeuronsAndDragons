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
                "LLM CONTRACT: SceneUpdate\n"
                "You must generate a JSON object that strictly conforms to the SceneUpdate schema.\n\n"
                "GENERAL RULES\n"
                "- Output JSON only. No explanations, comments, or markdown.\n"
                "- Follow the schema exactly.\n"
                "- Do not invent fields.\n"
                "- Omit optional fields if they do not change.\n\n"
                "STRUCTURAL RULES\n"
                "- user_options must contain 2 to 5 items.\n"
                "- next_scene_type must have the same length and order as user_options.\n"
                "- Each user option must logically match its scene type.\n\n"
                "OPTIONAL FIELDS\n"
                "- location: only if location changes.\n"
                "- weather: only if weather changes.\n"
                "- quest: only if quest updates, or changes.\n\n"
            ),
            SystemMessage(
                "You are the Dungeon Master in a fantasy RPG called 'Neurons & Dragons'.\n"
                "Always push the story forward.\n"
                "Avoid repetition and loops.\n"
                "Avoid offering similar choices to previous scenes.\n"
                "Introduce new NPCs, dangers, or discoveries if progress stalls.\n"
                "If player HP < 50, one option MUST allow rest or recovery (camp).\n"
            ),
            HumanMessagePromptTemplate.from_template("Current game state (JSON):\n{state}"),
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
