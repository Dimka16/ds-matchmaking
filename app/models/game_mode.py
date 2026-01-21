from enum import Enum


class GameMode(str, Enum):
    CLASSIC = 'classic'
    SOLO = 'solo'
    DUO = 'duo'
    BLITZ = 'blitz'
    TOURNAMENT = 'tournament'
