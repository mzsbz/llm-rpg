from pathlib import Path
from dotenv import load_dotenv

from llm_rpg.game.game import Game
from llm_rpg.game.game_config import GameConfig

_config_dir = Path(__file__).resolve().parents[2] / "config"

for env_file in [_config_dir / ".env", _config_dir / ".env.secret"]:
    load_dotenv(env_file)


if __name__ == "__main__":
    game = Game(config=GameConfig("config/game_config.yaml"))
    game.run()
