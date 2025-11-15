from pydantic import BaseModel, Field
from typing import List, Literal
from langchain_openai import ChatOpenAI

from rich.console import Console

from core import GameState
from core.save import SaveManager
from nodes.utils import get_player_choice


class DialogueUpdate(BaseModel):
    npc_name: str = Field(description="NPC name.")
    dialogue: str = Field(description="What the NPC says to the player in this turn.")
    summary: str = Field(description="One-line summary of what happened in the conversation.")
    player_choices: List[str] = Field(
        description="Available dialogue responses or actions the player can choose. 2–5 options."
    )
    next_scene_type: List[Literal["exploration", "combat", "dialogue"]] = Field(
        description="Scene type that follows each player choice, same length as player_choices."
    )


model = ChatOpenAI(model="gpt-5-nano", temperature=0.8).with_structured_output(DialogueUpdate)
console = Console()
save_manager = SaveManager()


def dialogue(state: GameState) -> GameState:
    state_str = state.model_dump_json()
    prompt = (
        "You are the Dungeon Master of 'Neurons & Dragons'.\n"
        "The player is now in a dialogue scene. Generate the NPC's dialogue lines, possible player responses, "
        "and how the scene can branch next. Keep it concise and immersive.\n"
        "Use the DialogueUpdate schema strictly.\n\n"
        f"Current game state:\n{state_str}\n"
    )

    response: DialogueUpdate = model.invoke(prompt)

    console.print("\n[bold cyan]🗣️ Dialogue begins[/bold cyan]\n")
    console.print(f"[yellow]{response.npc_name}:[/yellow] {response.dialogue}\n")

    for i, option in enumerate(response.player_choices, 1):
        console.print(f"{i}) {option}")
    console.print("")

    choice = get_player_choice("Your reply", len(response.player_choices))

    chosen_reply = response.player_choices[choice - 1]
    next_scene_type = response.next_scene_type[choice - 1]
    state.scene_type = next_scene_type
    state.history.append(f'npc: {response.summary}')
    state.history.append(f'player reply: {chosen_reply}')

    save_manager.save(state)
    return state
