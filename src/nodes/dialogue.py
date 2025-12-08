from pydantic import BaseModel, Field
from typing import List, Literal
from langchain_openai import ChatOpenAI

from rich.console import Console

from core import GameState
from core.save import SaveManager
from nodes.constants import MODEL_NAME
from nodes.utils import get_player_choice, list_available_player_choices


class DialogueUpdate(BaseModel):
    npc_name: str = Field(description="NPC name.")
    dialogue: str = Field(description="What the NPC says to the player in this turn.")
    summary: str = Field(description="One-line summary of what happened in the conversation.")
    player_choices: List[str] = Field(
        description="Available dialogue responses or actions the player can choose. 2–5 options."
    )
    next_scene_type: List[Literal["narration", "combat", "dialogue", "puzzle"]] = Field(
        description="Scene type that follows each player choice, same length as player_choices."
    )


model = ChatOpenAI(model=MODEL_NAME, temperature=0.8).with_structured_output(DialogueUpdate)
console = Console()


def dialogue(state: GameState) -> GameState:
    state_str = state.model_dump_json()
    prompt = (
        "You are the Dungeon Master in a fantasy text RPG called 'Neurons & Dragons'.\n"
        "The player is now in a dialogue scene. Generate the NPC's dialogue lines, possible player responses, "
        "and how the scene can branch next. Keep it concise and immersive.\n"
        "RULES:\n"
        "- Never repeat the exact same dialogue or player options from previous scenes.\n"
        "- Branching options must meaningfully change the situation.\n"
        "Use the DialogueUpdate schema strictly.\n\n"
        f"Current game state:\n{state_str}\n"
    )

    response: DialogueUpdate = model.invoke(prompt)

    console.print("\n[bold cyan]🗣️ Dialogue begins[/bold cyan]\n")
    console.print(f"[yellow]{response.npc_name}:[/yellow] {response.dialogue}\n")

    list_available_player_choices(choices=response.player_choices)
    choice = get_player_choice("Your reply", len(response.player_choices))

    chosen_reply = response.player_choices[choice - 1]
    next_scene_type = response.next_scene_type[choice - 1]
    state.scene_type = next_scene_type
    state.append_history(f"npc {response.npc_name}: {response.summary}")
    state.append_history(f"player reply: {chosen_reply}")

    SaveManager().save(state)
    return state
