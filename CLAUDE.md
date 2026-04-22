# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Run the game
uv run python -m llm_rpg

# Run tests
uv run pytest -s -v

# Run a single test file
uv run pytest tests/llm_rpg/systems/test_damage_calculator.py -s -v

# Install pre-commit hooks (run once after cloning)
uv run pre-commit install

# Run linting/formatting manually
uv run pre-commit run --all-files
```

## Environment Setup

Create `config/.env` with:
```
CEREBRAS_API_KEY=your_api_key_here
```

Sprite generation requires model files under `models/sprite/` (see README).

## Architecture

### Scene/State Machine

The game is a Pygame loop (`Game.run()`) that delegates entirely to a current `Scene`. Each scene owns a `current_state` (a `State` subclass) and delegates `handle_input`, `update`, and `render` to it. Scene transitions happen via `Game.change_scene(SceneTypes.*)`. States transition within a scene via `scene.change_state(...)`.

Scenes: `main_menu`, `hero_creation`, `resting_hub`, `battle`, `game_over`.

### Systems vs Scenes

`src/llm_rpg/systems/` contains pure game logic (no Pygame), organized into:
- `battle/` — damage calculation, action judging, narration, creativity tracking, enemy scaling, battle log
- `hero/` — Hero dataclass and inventory
- `generation/` — LLM-based enemy name/stat/sprite generation

`src/llm_rpg/scenes/` contains the Pygame rendering and input layer that drives those systems.

### LLM Layer

`LLM` is an abstract base with one concrete backend: `CerebrasLLM` (uses OpenAI-compatible API). It implements `generate_completion(prompt) -> str` and `generate_structured_completion(prompt, output_schema) -> BaseModel`. Each instance carries an `LLMCostTracker`; total cost is printed on exit.

LLM roles are configured in `config/game_config.yaml` under `action_judge`, `narrator`, `enemy_action`, and `enemy_generation`. Prompts are also stored in that file under the `prompts` key.

### Damage Calculation

Damage combines: base stat difference (attack vs defense), an LLM feasibility/potential-damage score, a creativity bonus/penalty (tracks overused words via `CreativityTracker`), and a random factor. All tuning values live in `config/game_config.yaml` under `damage_calculator`.

### Configuration

`config/game_config.yaml` is the single source of truth for all balance values, LLM model assignments, prompts, display settings, and sprite generation settings. `GameConfig` (in `src/llm_rpg/game/game_config.py`) loads and exposes these values to the `Game` object.

## Coding Rules (from AGENTS.md)

- No inline comments — explain in chat, not in code.
- Only add tests for core game logic calculations (see `tests/llm_rpg/systems/`).
- Do not add `__init__.py` files.
- Always use type hints on function parameters and return types.
- Keep `docs/` up to date when changing game systems (`docs/game_info.md` is the entry point).
