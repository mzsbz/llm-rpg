from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from llm_rpg.llm.llm import LLM
from llm_rpg.systems.battle.battle_log import BattleLog

if TYPE_CHECKING:
    from llm_rpg.systems.battle.enemy import Enemy
    from llm_rpg.systems.hero.hero import Hero


class PlayerActionGenerator(ABC):
    @abstractmethod
    def expand_action(
        self, raw_action: str, hero: Hero, enemy: Enemy, battle_log: BattleLog
    ) -> str:
        raise NotImplementedError


class LLMPlayerActionGenerator(PlayerActionGenerator):
    def __init__(self, llm: LLM, prompt: str, debug: bool = False):
        self.llm = llm
        self.prompt = prompt
        self.debug = debug

    def expand_action(
        self, raw_action: str, hero: Hero, enemy: Enemy, battle_log: BattleLog
    ) -> str:
        battle_log_string = battle_log.to_string_for_battle_ai()
        items_str = "\n".join(
            f"  - {item.name}: {item.description}"
            for item in hero.inventory.items
        )
        prompt = self.prompt.format(
            hero_name=hero.name,
            hero_description=hero.description,
            enemy_name=enemy.name,
            enemy_description=enemy.description,
            hero_items=items_str if items_str else "none",
            battle_log_string=battle_log_string,
            raw_action=raw_action,
        )
        if self.debug:
            print("++++++++ DEBUG PlayerAction prompt ++++++++")
            print(prompt)
            print("=" * 50)
        output = self.llm.generate_completion(prompt)
        if self.debug:
            print("-------- DEBUG PlayerAction output --------")
            print(output)
            print("=" * 50)
        return output
