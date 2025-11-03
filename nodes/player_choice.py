from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from rich.console import Console
from rich.prompt import Prompt

from core import GameState


load_dotenv()

console = Console()
model = ChatOpenAI(model="gpt-5-nano", temperature=0.9)


def player_choice(state: GameState) -> GameState:
    choice = Prompt.ask("\nChoose your action (1/2/3)").strip()
    state.history.append(f'"player_action": {choice}')
    return state
