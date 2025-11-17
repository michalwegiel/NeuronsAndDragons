from itertools import islice

from pydantic import BaseModel, Field
from typing import Literal, Optional
from langchain_openai import ChatOpenAI

from rich.console import Console

from core import GameState
from core.save import SaveManager
from nodes.constants import MODEL_NAME
from nodes.utils import get_player_choice, list_available_player_choices


class ExplorationUpdate(BaseModel):
    description: str = Field(description="Narrative description of the environment and situation the player explores.")
    player_actions: list[str] = Field(
        description="Available actions the player can take. 2–5 options."
    )
    next_scene_type: list[Literal["narration", "exploration", "combat", "dialogue"]] = Field(
        description="Scene type that follows each player action, same length as player_actions."
    )
    discoveries: Optional[list[str]] = Field(
        default=None,
        description="Optional items or clues the player can find in this scene (0-3)."
    )
    summary: str = Field(description="One-line summary of what happened in this exploration turn.")


model = ChatOpenAI(model=MODEL_NAME, temperature=0.8).with_structured_output(ExplorationUpdate)
console = Console()


def exploration(state: GameState) -> GameState:
    state_str = state.model_dump_json()
    prompt = (
        "You are the Dungeon Master of 'Neurons & Dragons'.\n"
        "The player is now in an exploration scene. Describe the surroundings, "
        "possible actions, any items, clues, or puzzles the player can discover, "
        "and how the scene can branch next. Keep it immersive and consequential.\n"
        "HARD RULES (must follow exactly):\n"
        "1) Provide 2–5 player_actions total.\n"
        "2) next_scene_type must be the same length as player_actions and match by index.\n"
        "3) In this turn, at least one next_scene_type MUST be one of: narration, combat, dialogue (i.e., not exploration).\n"
        "4) No more than 50% of next_scene_type entries may be 'exploration'.\n"
        "5) If the last two scene types were 'exploration', then:\n"
        "   - Provide AT LEAST two non-exploration next_scene_type options, and\n"
        "   - Prefer 'narration' or 'dialogue' to advance the plot.\n"
        "6) Advance the main story or world state in a meaningful way in this turn.\n"
        "7) Do NOT repeat discoveries, clues, puzzles, or gated areas already encountered.\n"
        "8) Keep momentum: avoid loops like 'explore deeper' repeatedly unless it introduces a clearly new objective, risk, or reward.\n"
        "9) Use the ExplorationUpdate schema strictly.\n\n"
        "Scene mix targets (soft): narration ~40%, dialogue ~30%, combat ~20%, exploration ≤10–30% depending on pacing.\n"
        "If the recent scenes contain a lot of exploration, bias strongly toward narration/dialogue now.\n"
        "If a threat is imminent, allow combat as a branch but not the only non-exploration option.\n\n"
        f"Current game state (JSON):\n{state_str}\n"
        f"\nRecent events (last 10):\n{list(islice(state.history, 10))}\n"
    )

    response: ExplorationUpdate = model.invoke(prompt)

    console.print("\n[bold cyan]🧭 Exploration begins[/bold cyan]\n")
    console.print(f"{response.description}\n")
    if response.discoveries:
        console.print("[magenta]You notice the following discoveries:[/magenta]")
        for discovery in response.discoveries:
            console.print(f"- {discovery}")
        console.print("")

    list_available_player_choices(choices=response.player_actions)
    choice = get_player_choice("Your action", len(response.player_actions))

    chosen_action = response.player_actions[choice - 1]
    next_scene_type = response.next_scene_type[choice - 1]
    state.scene_type = next_scene_type
    state.history.append(f"exploration: {response.summary}")
    if response.discoveries:
        state.history.append(f"discoveries: {', '.join(response.discoveries)}")
    state.history.append(f"player action: {chosen_action}")

    SaveManager().save(state)
    return state
