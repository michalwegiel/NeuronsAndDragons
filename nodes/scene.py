import json

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from rich.console import Console

from core import GameState


load_dotenv()

console = Console()
model = ChatOpenAI(model="gpt-5-nano", temperature=0.9)


def dm_scene(state: GameState) -> GameState:
    state_str = json.dumps(state, indent=2, default=vars)
    prompt = (
        "You are the Dungeon Master in our fantasy text‐RPG 'Neurons & Dragons'.\n"
        "Here is the current game state:\n"
        f"{state_str}\n"
        "Narrate the next scene (1-3 paragraphs) and present 3 numbered choices for the player."
    )

    resp = model.invoke(prompt)
    console.print("\n" + resp.content)
    state.history.append(f'"dm": {resp.content}')
    return state
