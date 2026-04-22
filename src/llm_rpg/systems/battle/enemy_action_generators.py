from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from llm_rpg.llm.llm import LLM
from llm_rpg.systems.battle.battle_log import BattleLog

if TYPE_CHECKING:
    from llm_rpg.systems.battle.enemy import Enemy
    from llm_rpg.systems.hero.hero import Hero


class EnemyActionGenerator(ABC):
    @abstractmethod
    def generate_next_action(
        self, enemy: Enemy, hero: Hero, battle_log: BattleLog
    ) -> str:
        raise NotImplementedError


class LLMEnemyActionGenerator(EnemyActionGenerator):
    def __init__(self, llm: LLM, prompt: str, debug: bool = False):
        self.llm = llm
        self.prompt = prompt
        self.debug = debug

    def generate_next_action(
        self, enemy: Enemy, hero: Hero, battle_log: BattleLog
    ) -> str:
        battle_log_string = battle_log.to_string_for_battle_ai()
        enemy_stats = enemy.get_current_stats()
        hero_stats = hero.get_current_stats()
        hero_items_str = "\n".join(
            f"  - {item.name}: {item.description}"
            for item in hero.inventory.items
        )
        prompt = self.prompt.format(
            self_name=enemy.name,
            self_description=enemy.description,
            self_archetype=enemy.archetype.value,
            self_hp=enemy.hp,
            self_max_hp=enemy_stats.max_hp,
            self_attack=enemy_stats.attack,
            self_defense=enemy_stats.defense,
            self_focus=enemy_stats.focus,
            hero_name=hero.name,
            hero_class=hero.class_name,
            hero_description=hero.description,
            hero_hp=hero.hp,
            hero_max_hp=hero_stats.max_hp,
            hero_attack=hero_stats.attack,
            hero_defense=hero_stats.defense,
            hero_focus=hero_stats.focus,
            hero_items=hero_items_str if hero_items_str else "none",
            battle_log_string=battle_log_string,
        )
        if self.debug:
            print("++++++++ DEBUG EnemyAction prompt ++++++++")
            print(prompt)
            print("=" * 50)
        output = self.llm.generate_completion(prompt)
        if self.debug:
            print("-------- DEBUG EnemyAction output --------")
            print(output)
            print("=" * 50)
        return output
