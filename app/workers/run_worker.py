import os
import sys
from app.models.game_mode import GameMode
from app.workers.worker import MatchmakingWorker


def main():
    mode = os.getenv("WORKER_MODE")
    if not mode:
        print("WORKER_MODE is required (classic|duo|tournament)")
        sys.exit(1)

    worker = MatchmakingWorker(GameMode(mode))
    worker.start()


if __name__ == "__main__":
    main()