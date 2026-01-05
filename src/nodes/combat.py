import random
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import Optional, List

from rich.console import Console
from rich.prompt import Prompt

from core import GameState
from core.entities import Enemy, Item, Weapon, Potion, Armor, Player
from core.entities.enemy import SpecialAttack
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


class UI:
    def __init__(self):
        self.console = Console()

    def combat_intro(self, enemy: Enemy, narrative: str) -> None:
        self.console.print(f"\n[bold red]⚔️ {enemy.name} appears![/bold red]")
        self.console.print(narrative + "\n")
        self.console.print(f"[dim]{enemy.description}[/dim]\n")

    def display_status(self, player: Player, enemy: Enemy) -> None:
        self.console.print(
            f"[green]Your HP:[/green] {player.hp} | "
            f"[red]{enemy.name} HP:[/red] {enemy.hp} | "
            f"[yellow]Potions: {len(player.inventory.potions)}[/yellow]\n"
        )

    @staticmethod
    def choose_action() -> str:
        return Prompt.ask("Choose your action", choices=["attack", "use potion", "run"], default="attack")

    def attack(self, enemy: Enemy, weapon: Weapon, dmg: int) -> None:
        self.console.print(
            f"You strike {enemy.name} {f'with your {weapon.name} ' if weapon is not None else ''}"
            f"for [bold]{dmg}[/bold] damage!"
        )

    def enemy_attack(self, enemy: Enemy, dmg: int, critical_hit: bool) -> None:
        if critical_hit:
            self.console.print(f"[bold red]{enemy.name} lands a CRITICAL HIT for {dmg} damage!![/bold red]\n")
        else:
            self.console.print(f"[red]{enemy.name} attacks you for {dmg} damage![/red]\n")

    def enemy_special_attack(self, enemy: Enemy, dmg: int, special_attack: SpecialAttack, critical_hit: bool) -> None:
        if critical_hit:
            self.console.print("[bold red]CRITICAL HIT!!![/bold red]")
        self.console.print(f"[bold magenta]{enemy.name} uses SPECIAL ATTACK: {special_attack.name}![/bold magenta]")
        self.console.print(f"[magenta]{special_attack.description} It deals {dmg} damage![/magenta]\n")

    def potion(self, heal: int | None) -> None:
        if heal is not None:
            self.console.print(f"You drink a potion and recover [green]{heal}[/green] HP.")
        else:
            self.console.print("[red]No potions left![/red]")

    def run(self, result: bool) -> None:
        if result:
            self.console.print("[yellow]You manage to flee safely![/yellow]")
        else:
            self.console.print("[red]You fail to escape![/red]")

    def player_defeat(self, lost_weapon: Weapon) -> None:
        self.console.print("[bold red]💀 You have been defeated![/bold red]")
        if lost_weapon:
            self.console.print(f"[bold red]You have lost {lost_weapon.name}![/bold red]")

    def player_victory(self, enemy: Enemy) -> None:
        self.console.print(f"[bold green]🏆 You defeated {enemy.name}![/bold green]")

    def loot_info(self) -> None:
        self.console.print("\n[bold yellow]You find some loot:[/bold yellow]")

    def show_loot_item(self, item: Item) -> None:
        self.console.print(f"• {item.name} ({item.rarity}) - {item.description or ''}")


model = ChatOpenAI(model="gpt-5-nano", temperature=0.7).with_structured_output(CombatSetup)
ui = UI()


def is_critical_hit(critical_chance: int) -> bool:
    return random.randint(1, 100) <= critical_chance


def attack(player: Player, enemy: Enemy) -> None:
    player_dmg = player.calc_attack()
    weapon = player.main_weapon()
    dmg = dice_roll("1d20") + player_dmg
    enemy.hp -= dmg
    ui.attack(enemy=enemy, weapon=weapon, dmg=dmg)


def enemy_normal_attack(player: Player, enemy: Enemy) -> None:
    player_defense = player.calc_defense()
    is_critical = is_critical_hit(critical_chance=enemy.critical_hit_chance)
    dmg_modifier = 2 if is_critical else 1
    dmg = round(dice_roll(f"{enemy.attacks_per_turn}d{enemy.attack_max}") * dmg_modifier * (1 - player_defense / 25))
    player.damage(dmg)
    ui.enemy_attack(enemy=enemy, dmg=dmg, critical_hit=is_critical)


def enemy_special_attack(player: Player, enemy: Enemy, special_attack: SpecialAttack) -> None:
    player_defense = player.calc_defense()
    is_critical = is_critical_hit(critical_chance=enemy.critical_hit_chance)

    critical_hit_dmg_modifier = 2 if is_critical else 1
    special_attack_dmg_modifier = special_attack.dmg_multiplier
    dmg_modifier = critical_hit_dmg_modifier * special_attack_dmg_modifier
    dmg = round(dice_roll(f"1d{enemy.attack_max}") * dmg_modifier * (1 - player_defense / 25))
    player.damage(dmg)
    enemy.reset_special_attack_cooldown(special_attack=special_attack)

    ui.enemy_special_attack(enemy=enemy, dmg=dmg, special_attack=special_attack, critical_hit=is_critical)


def enemy_attack(player: Player, enemy: Enemy) -> None:
    special_attack = enemy.pick_special_attack()
    if special_attack:
        enemy_special_attack(player=player, enemy=enemy, special_attack=special_attack)
    enemy_normal_attack(player=player, enemy=enemy)
    enemy.reduce_special_attacks_cooldown()


def potion(player: Player) -> None:
    heal = None
    if len(player.inventory.potions) > 0:
        pot = player.inventory.potions.pop()
        heal = pot.potency
        player.heal(heal)
    ui.potion(heal=heal)


def run(player: Player, enemy: Enemy) -> bool:
    player_escape = player.calc_escape()
    result = False
    if dice_roll("1d20") + player_escape >= enemy.escape_difficulty:
        result = True
    ui.run(result=result)
    return result


def combat(state: GameState) -> GameState:
    state_str = state.model_dump_json()
    prompt = (
        "You are the Dungeon Master in a fantasy text RPG called 'Neurons & Dragons'.\n"
        "The player is about to enter combat.\n"
        "Generate the enemy they are about to face, the introduction narrative, and possible loot.\n"
        "Difficulty rules:\n"
        "- Enemy should be reasonably beatable and scale approximately to the player’s current power. "
        "However, if the story context suggests arrogance, risk, curiosity, warnings ignored, "
        "or a clearly dangerous location or enemy type, then it is valid (and narratively appropriate) "
        "for the enemy to be significantly stronger. In such cases, emphasize the danger in the narrative "
        "and make it clear that the player may attempt to fight or retreat.\n"
        "Output strictly using the CombatSetup schema (no extra fields, no commentary).\n\n"
        f"Current game state:\n{state_str}\n"
    )

    setup: CombatSetup = model.invoke(prompt)
    player = state.player
    enemy = setup.enemy
    narrative = setup.narrative

    ui.combat_intro(enemy=enemy, narrative=narrative)

    while player.hp > 0 and enemy.hp > 0:
        ui.display_status(player=player, enemy=enemy)
        action = ui.choose_action()
        if action == "attack":
            attack(player=player, enemy=enemy)
        elif action == "use potion":
            potion(player=player)
            continue
        elif action == "run":
            result = run(player=player, enemy=enemy)
            if result:
                state.scene_type = "narration"
                state.append_history("Player fled from combat")
                return state

        if enemy.hp > 0:
            enemy_attack(player=player, enemy=enemy)

    if player.hp <= 0:
        lost_weapon = player.drop_weapon()
        ui.player_defeat(lost_weapon=lost_weapon)
        state.append_history(f"Player was defeated by {enemy.name}")
    else:
        ui.player_victory(enemy=enemy)
        player.gain_experience(amount=100)
        state.append_history(f"Player defeated {enemy.name}")

        if setup.loot:
            ui.loot_info()
            for item in setup.loot:
                ui.show_loot_item(item=item)
                state.player.add_item(item=item)
            state.append_history(f"Loot obtained: {[item.name for item in setup.loot]}")

    state.scene_type = "narration"
    SaveManager().save(state)
    return state
