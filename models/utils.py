from enum import Enum


class States(Enum):
    IDDLE = 1
    ATTACKING = 2
    KNOCKBACK = 3
    RECOILING = 4
    SPAWNING = 5
    WALKING = 6
    JUMPING = 7
    FALLING = 8
    DEAD = 9


class Orientation(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4
    NEUTRAL = 5

class AttackState(Enum):
    BUILDUP = "buildup_phase"
    ACTIVE = "active_phase"
    RECOVERY = "recovery_phase"
    

class GameState(Enum):

    MAIN_MENU = 1
    PLAYING = 2
    PAUSE = 3
    SPAWNING = 4
    GAME_OVER = 5
    VICTORY = 6
    TRANSITION = 7


class Position(Enum):
    GROUND_RIGHT_EDGE = "ground_right_edge"
    MIDDLE_RIGHT_EDGE = "1/2_right_edge"
    GROUND_LEFT_EDGE = "ground_left_edge"
    MIDDLE_LEFT_EDGE = "1/2_left_edge"
    QUARTER_TOP_EDGE = "1/4_top_edge"
    MIDDLE_TOP_EDGE = "1/2_top_edge"
    THREE_QUARTER_TOP_EDGE = "1/8_top_edge"
