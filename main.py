import json
from rich.console import Console
from rich.prompt import Prompt

from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from dotenv import load_dotenv

load_dotenv()


console = Console()
MODEL = "gpt-5-nano"

# TODO: option to select class and name
# TODO: random location and weather
game_state = {
    "player": {
        "name": "Michal",
        "class": "Ranger",
        "hp": 100,
        "inventory": ["dagger", "healing potion"],
        "location": "Dark Forest Entrance",
    },
    "world": {
        "time": "dusk",
        "weather": "foggy",
    },
    "history": [],
}


model = ChatOpenAI(model=MODEL, temperature=0.9)


def dm_scene(state: dict) -> dict:
    state_str = json.dumps(state, indent=2)
    prompt = (
        "You are the Dungeon Master in our fantasy text‐RPG 'Neurons & Dragons'.\n"
        "Here is the current game state:\n"
        f"{state_str}\n"
        "Narrate the next scene (2-3 paragraphs) and present 3 numbered choices for the player."
    )

    resp = model.invoke(prompt)
    console.print("\n" + resp.content)
    state["history"].append({"dm": resp.content})
    return state


def player_choice(state: dict) -> dict:
    choice = Prompt.ask("\nChoose your action (1/2/3)").strip()
    state["history"].append({"player_action": choice})
    # TODO: Update state (HP, inventory, location) based on choice
    return state


graph = StateGraph(dict)
graph.add_node("scene", dm_scene)
graph.add_node("choice", player_choice)

graph.add_edge("scene", "choice")
graph.add_edge("choice", "scene")
graph.add_edge("scene", END)

graph.set_entry_point("scene")
runnable = graph.compile()


def main():
    console.print("[bold green]🧙 Welcome to Neurons & Dragons![/bold green]")
    while True:
        runnable.invoke(game_state)


if __name__ == "__main__":
    main()
