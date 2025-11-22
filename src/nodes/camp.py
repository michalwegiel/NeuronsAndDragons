from typing import Literal

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from rich.console import Console

from core import GameState
from core.save import SaveManager
from nodes.constants import MODEL_NAME
from nodes.utils import get_player_choice, list_available_player_choices


class CampUpdate(BaseModel):
    narrative: str = Field(description="Story text to display to the player.")
    summary: str = Field(description="One line summary of scene narrative. Used for history aggregation.")
    user_options: list[str] = Field(
        description=(
            "List of possible actions choices the player can take next. "
            "Each option should be a short, self-contained string describing the action. "
            "Depending on situation, user should have at least 2 options and no more than 5."
        )
    )
    next_scene_type: list[Literal["narration", "dialogue"]] = Field(
        description=(
            "A list of appropriate scene types that should occur based on player choice. "
            "Each user option should have corresponding outcome scene type. "
            "Used by the engine to branch the story."
        ),
    )


console = Console()
model = ChatOpenAI(model=MODEL_NAME, temperature=0.5).with_structured_output(CampUpdate)


def camp(state: GameState) -> GameState:
    state_str = state.model_dump_json()
    prompt = (
        "You are the Dungeon Master in a fantasy text RPG called 'Neurons & Dragons'.\n"
        "Generate a *camp scene*.\n"
        "The player is resting at a safe place (a camp, fire, ruins, cave, etc.).\n"
        "Camp scenes should feel calm, introspective, or atmospheric, with a small story twist.\n\n"
        "ALLOWED ACTIONS for camp scenes:\n"
        "- Rest and regain health.\n"
        "- Reflect, meditate, or experience a dream.\n"
        "- Trigger a mysterious or prophetic dialogue (dream, vision, memory, spirit).\n\n"
        "RULES:\n"
        "- Provide 2–4 user_options.\n"
        "- next_scene_type MUST have same length as user_options.\n"
        "- Scene types allowed from camp: ['narration', 'dialogue'].\n"
        "- Move the story forward gently.\n\n"
        "Respond strictly following the CampUpdate schema.\n\n"
        f"Current game state:\n{state_str}\n"
    )

    response: CampUpdate = model.invoke(prompt)

    console.print(f"\n{response.narrative}\n")

    before = state.player.hp
    state.player.heal(50)
    restored = state.player.hp - before
    console.print(f"[green]You recover {restored} HP.[/green]\n")

    state.history.append(f"dungeon master: {response.summary}")

    list_available_player_choices(choices=response.user_options)
    choice = get_player_choice("Your action", len(response.user_options))

    state.scene_type = response.next_scene_type[choice - 1]
    state.history.append(f"player action: {response.user_options[choice - 1]}")

    SaveManager().save(state)
    return state
