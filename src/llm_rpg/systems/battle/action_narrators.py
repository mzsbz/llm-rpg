from __future__ import annotations

from abc import ABC, abstractmethod

from llm_rpg.llm.llm import LLM
from llm_rpg.systems.battle.action_judges import ActionJudgment
from llm_rpg.systems.battle.enemy import Enemy
from llm_rpg.systems.hero.hero import Hero


class ActionNarrator(ABC):
    @abstractmethod
    def describe_action(
        self,
        proposed_action_attacker: str,
        hero: Hero,
        enemy: Enemy,
        is_hero_attacker: bool,
        judgment: ActionJudgment,
        total_damage: int,
    ) -> str:
        raise NotImplementedError


class LLMActionNarrator(ActionNarrator):
    def __init__(self, llm: LLM, prompt: str, debug: bool = False):
        self.llm = llm
        self.prompt = prompt
        self.debug = debug
        self._snap_steps = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
        self._feasibility_labels = {
            0.0: "impossible",
            0.2: "low",
            0.4: "medium",
            0.6: "high",
            0.8: "very high",
            1.0: "certain",
        }
        self._damage_labels = {
            0.0: "no damage",
            0.2: "low",
            0.4: "medium",
            0.6: "high",
            0.8: "very high",
            1.0: "maximum",
        }

    def _sanitize_text(self, text: str) -> str:
        text = text.replace("’", "'")
        allowed = {"'", ".", "?", "!"}
        filtered = "".join(
            [
                char if char.isalpha() or char.isspace() or char in allowed else " "
                for char in text
            ]
        )
        return " ".join(filtered.split())

    def _snap_score(self, value: float) -> float:
        clamped = max(0.0, min(1.0, value))
        return min(self._snap_steps, key=lambda step: abs(step - clamped))

    def _label_feasibility(self, value: float) -> str:
        snapped = self._snap_score(value)
        return self._feasibility_labels[snapped]

    def _label_damage(self, value: float) -> str:
        snapped = self._snap_score(value)
        return self._damage_labels[snapped]

    def _get_prompt(
        self,
        hero: Hero,
        enemy: Enemy,
        is_hero_attacker: bool,
        proposed_action_attacker: str,
        judgment: ActionJudgment,
        total_damage: int,
    ) -> str:
        if is_hero_attacker:
            attacker_name = hero.name
            defender_name = enemy.name
        else:
            attacker_name = enemy.name
            defender_name = hero.name
        return self.prompt.format(
            attacker_name=attacker_name,
            defender_name=defender_name,
            proposed_action_attacker=proposed_action_attacker,
            feasibility=self._label_feasibility(judgment.feasibility),
            potential_damage=self._label_damage(judgment.potential_damage),
            total_damage=total_damage,
        )

    def describe_action(
        self,
        proposed_action_attacker: str,
        hero: Hero,
        enemy: Enemy,
        is_hero_attacker: bool,
        judgment: ActionJudgment,
        total_damage: int,
    ) -> str:
        prompt = self._get_prompt(
            hero=hero,
            enemy=enemy,
            is_hero_attacker=is_hero_attacker,
            proposed_action_attacker=proposed_action_attacker,
            judgment=judgment,
            total_damage=total_damage,
        )
        if self.debug:
            print("++++++++ DEBUG ActionNarrator prompt ++++++++")
            print(prompt)
            print("=" * 10)
        output = self.llm.generate_completion(prompt=prompt)
        if self.debug:
            print("-------- DEBUG ActionNarrator output --------")
            print(output)
            print("=" * 10)
        return self._sanitize_text(output)
