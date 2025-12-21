from app.models.player import Player
from app.repositories.waiting_player_repo_impl import WaitingPlayerRepositoryImpl
from app.services.matchmaking_strategy_classic_impl import ClassicMatchmakingStrategy

repo = WaitingPlayerRepositoryImpl(elo_threshold=100)
strategy = ClassicMatchmakingStrategy(repo)

p1 = Player(1, "ana", 1400, "EU")
p2 = Player(2, "eva", 1450, "EU")
p3 = Player(3, "iva", 1700, "EU")

print(strategy.handle_player(p1))
print(strategy.handle_player(p2))
print(strategy.handle_player(p3))
