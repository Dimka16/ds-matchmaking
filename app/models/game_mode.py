from enum import Enum


class GameMode(str, Enum):
    CLASSIC = 'classic'
    DUO = 'duo'
    TOURNAMENT = 'tournament'
