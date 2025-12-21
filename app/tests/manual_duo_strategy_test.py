from app.models.player import Player
from app.repositories.waiting_player_repo_impl import WaitingPlayerRepositoryImpl
from app.services.matchmaking_strategy_duo_impl import DuoMatchmakingStrategy


def test_duo_match_created_when_four_players_join():
    repo = WaitingPlayerRepositoryImpl()
    strategy = DuoMatchmakingStrategy(repo)

    players = [
        Player(1, "p1", 1200, "EU"),
        Player(2, "p2", 1210, "EU"),
        Player(3, "p3", 1220, "EU"),
        Player(4, "p4", 1230, "EU"),
    ]

    match = None
    for p in players:
        match = strategy.handle_player(p)
        print(match)

    assert match is not None
    assert len(match.players) == 4


def test_duo_not_created_with_less_than_four_players():
    repo = WaitingPlayerRepositoryImpl()
    strategy = DuoMatchmakingStrategy(repo)

    p1 = Player(1, "p1", 1200, "EU")
    p2 = Player(2, "p2", 1210, "EU")

    assert strategy.handle_player(p1) is None
    assert strategy.handle_player(p2) is None
