import json
from rich.console import Console
from rich.prompt import Prompt

from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from dotenv import load_dotenv

from core import GameState
from core.entities import Player, PlayerClass, Race, Origin, World

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


def player_choice(state: GameState) -> GameState:
    choice = Prompt.ask("\nChoose your action (1/2/3)").strip()
    state.history.append(f'"player_action": {choice}')
    # TODO: Update state (HP, inventory, location) based on choice
    return state


graph = StateGraph(GameState)
graph.add_node("scene", dm_scene)
graph.add_node("choice", player_choice)

graph.add_edge("scene", "choice")
graph.add_edge("choice", "scene")
graph.add_edge("scene", END)

graph.set_entry_point("scene")
runnable = graph.compile()


def main():
    game_state = GameState(
        player=Player(
            name="Michal",
            player_class=PlayerClass.BARBARIAN,
            race=Race.GNOME,
            origin=Origin.CRIMINAL,
            inventory=["knife"]
        ),
        world=World(location="Emerald Forest", quest="Find the lost relic"),
        history=["The adventure begins!"]
    )
    console.print("[bold green]🧙 Welcome to Neurons & Dragons![/bold green]")
    while True:
        runnable.invoke(game_state)


if __name__ == "__main__":
    main()
