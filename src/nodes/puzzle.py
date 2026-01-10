from typing import List, Literal

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from rich.console import Console

from core import GameState
from core.save import SaveManager
from nodes.constants import MODEL_NAME
from nodes.utils import list_available_player_choices, get_player_choice


class PuzzleOption(BaseModel):
    text: str = Field(description="The attempt or answer available to the player.")
    correct: bool = Field(description="Whether this option solves the puzzle.")
    next_scene_type: Literal["narration", "combat", "dialogue"] = Field(
        description="Scene type triggered if this option is chosen."
    )


class PuzzleUpdate(BaseModel):
    narrative: str = Field(description="Description of the puzzle environment and the puzzle itself.")
    puzzle_prompt: str = Field(
        description="The riddle, mechanism description, or puzzle challenge presented to the player."
    )
    summary: str = Field(description="One-line summary for history.")
    options: List[PuzzleOption] = Field(description="Possible answers/attempts. At least 2, at most 5.")


console = Console()
model = ChatOpenAI(model=MODEL_NAME, temperature=1.0).with_structured_output(PuzzleUpdate)


def puzzle(state: GameState) -> GameState:
    state_str = state.model_dump_json()
    prompt = (
        "You are the Dungeon Master in a fantasy text RPG called 'Neurons & Dragons'.\n"
        "Generate a PUZZLE scene.\n\n"
        "GENERAL RULES:\n"
        "- Output JSON only.\n"
        "- Do not include explanations or commentary.\n"
        "- Follow the schema exactly.\n"
        "- Do not include solution explanations.\n"       
        "PUZZLE DESIGN RULES:\n"
        "- The puzzle must be solvable using logic or observation from the text.\n"
        "- Do not reveal which option is correct.\n"
        "- All options must sound plausible.\n"
        "- Avoid trivia or real-world knowledge.\n"
        "EXTRA RULES:\n"
        "- Provide a clear riddle or puzzle challenge.\n"
        "- Provide 2–5 options.\n"
        "- EXACTLY ONE of the options must have correct=true.\n"
        "- Wrong answers should still meaningfully branch the story (different scene types allowed).\n"
        "- next_scene_type must reflect the consequences.\n"
        "- Allowed next scenes: narration, combat, dialogue.\n"
        "- If puzzle is successfully solved, story should progress.\n"
        "- Avoid repeating puzzles from history, ALWAYS come up with a new puzzle.\n"
        "- Respond strictly using PuzzleUpdate schema.\n\n"
        f"Current game state:\n{state_str}\n"
    )

    response: PuzzleUpdate = model.invoke(prompt)

    console.print(f"\n{response.narrative}\n")
    console.print(f"[yellow]{response.puzzle_prompt}[/yellow]\n")

    state.append_history(f"dungeon master: {response.summary}")
    state.append_history(f"puzzle: {response.puzzle_prompt}")

    list_available_player_choices(choices=[option.text for option in response.options])
    choice = get_player_choice("Your answer", len(response.options))
    choice = response.options[choice - 1]
    state.append_history(f"player action: {choice.text}")

    if choice.correct:
        console.print("[green]You solved the puzzle![/green]\n")
        state.append_history("player solved the puzzle")
        state.player.gain_experience(amount=100)
    else:
        console.print("[red]Your attempt fails.[/red]\n")
        state.append_history("player failed to solve the puzzle")

    state.scene_type = choice.next_scene_type

    SaveManager().save(state)
    return state
