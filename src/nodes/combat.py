from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import Optional, List

from rich.console import Console
from rich.prompt import Prompt

from core import GameState
from core.entities import Enemy, Item, Weapon, Potion, Armor, Player
from core.save import SaveManager
from nodes.utils import dice_roll

load_dotenv()


class CombatSetup(BaseModel):
    narrative: str = Field(description="Story introduction to the fight, setting the mood and tension")
    enemy: Enemy = Field(description="Enemy statistics and description")
    loot: Optional[List[Item | Weapon | Armor | Potion]] = Field(
        default=None,
        description=(
            "A list of items that may drop after a victory (0-3 items), "
            "often nothing of value, but sometimes a real 'treasure'"
        ),
    )


model = ChatOpenAI(model="gpt-5-nano", temperature=0.7).with_structured_output(CombatSetup)
console = Console()


def attack(player: Player, enemy: Enemy) -> None:
    player_dmg = player.calc_attack()
    weapon = player.main_weapon()
    dmg = dice_roll("1d20") + player_dmg
    enemy.hp -= dmg
    console.print(
        f"You strike {enemy.name} {f'with your {weapon.name} ' if weapon is not None else ''}"
        f"for [bold]{dmg}[/bold] damage!"
    )


def enemy_attack(player: Player, enemy: Enemy) -> None:
    player_defense = player.calc_defense()
    dmg = round(dice_roll(f"1d{enemy.attack_max}") * (1 - player_defense / 25))
    player.damage(dmg)
    console.print(f"[red]{enemy.name} attacks you for {dmg} damage![/red]\n")


def potion(player: Player) -> None:
    if len(player.inventory.potions) > 0:
        pot = player.inventory.potions.pop()
        heal = pot.potency
        player.heal(heal)
        console.print(f"You drink a potion and recover [green]{heal}[/green] HP.")
    else:
        console.print("[red]No potions left![/red]")


def run(player: Player, enemy: Enemy) -> bool:
    player_escape = player.calc_escape()
    if dice_roll("1d20") + player_escape >= enemy.escape_difficulty:
        console.print("[yellow]You manage to flee safely![/yellow]")
        return True
    console.print("[red]You fail to escape![/red]")
    return False


def combat(state: GameState) -> GameState:
    state_str = state.model_dump_json()
    prompt = (
        "You are the Dungeon Master in a fantasy text RPG called 'Neurons & Dragons'.\n"
        "The player is about to enter combat.\n"
        "Generate the enemy they are about to face, the introduction narrative, and possible loot.\n"
        "Adjust difficulty to feel fair based on game state.\n"
        "Respond using the CombatSetup schema.\n\n"
        f"Current game state:\n{state_str}\n"
    )

    setup: CombatSetup = model.invoke(prompt)

    console.print(f"\n[bold red]⚔️ {setup.enemy.name} appears![/bold red]")
    console.print(setup.narrative + "\n")
    console.print(f"[dim]{setup.enemy.description}[/dim]\n")

    player = state.player
    enemy = setup.enemy

    while player.hp > 0 and enemy.hp > 0:
        console.print(f"[green]Your HP:[/green] {player.hp} | [red]{enemy.name} HP:[/red] {enemy.hp}\n")

        action = Prompt.ask("Choose your action", choices=["attack", "use potion", "run"], default="attack")

        if action == "attack":
            attack(player=player, enemy=enemy)
        elif action == "use potion":
            potion(player=player)
        elif action == "run":
            result = run(player=player, enemy=enemy)
            if result:
                state.scene_type = "narration"
                state.history.append("Player fled from combat")
                return state

        if enemy.hp > 0:
            enemy_attack(player=player, enemy=enemy)

    if player.hp <= 0:
        console.print("[bold red]💀 You have been defeated![/bold red]")
        state.history.append(f"Player was defeated by {enemy.name}")
    else:
        console.print(f"[bold green]🏆 You defeated {enemy.name}![/bold green]")
        state.history.append(f"Player defeated {enemy.name}")

        if setup.loot:
            console.print("\n[bold yellow]You find some loot:[/bold yellow]")
            for item in setup.loot:
                console.print(f"• {item.name} ({item.rarity}) - {item.description or ''}")
                state.player.add_item(item)
            state.history.append(f"Loot obtained: {[item.name for item in setup.loot]}")

    state.scene_type = "narration"
    SaveManager().save(state)
    return state
