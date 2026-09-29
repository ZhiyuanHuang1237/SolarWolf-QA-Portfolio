"""SolarWolf 白盒自动化：飞船、火球与特殊道具的移动逻辑。"""

import os
import sys
from pathlib import Path

import pytest


os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
# 被测游戏源码与 QA 作品集位于同一工作区的不同目录。
GAME_SOURCE = Path(__file__).resolve().parents[2] / "solarwolf" / "solarwolf"
if str(GAME_SOURCE) not in sys.path:
    sys.path.insert(0, str(GAME_SOURCE))

import pygame  # noqa: E402
import game  # noqa: E402
import objship  # noqa: E402
import objshot  # noqa: E402
import objpowerup  # noqa: E402


@pytest.fixture(autouse=True)
def isolated_movement_state(monkeypatch):
    pygame.init()
    ship_image = pygame.Surface((10, 10))
    fireball_image = pygame.Surface((6, 6))
    monkeypatch.setattr(objship, "shipimages", [[ship_image] for _ in range(8)])
    monkeypatch.setattr(objshot, "images", [fireball_image])
    monkeypatch.setattr(objshot.gfx, "rect", pygame.Rect(0, 0, 100, 100))
    monkeypatch.setattr(game, "arena", pygame.Rect(0, 0, 100, 100))
    monkeypatch.setattr(game, "ship_slowspeed", 10)
    monkeypatch.setattr(game, "ship_fastspeed", 20)
    monkeypatch.setattr(game, "thruster", 0)


@pytest.mark.parametrize(
    ("command", "expected_move", "expected_image"),
    [
        ("cmd_up", [0, -1], 0),
        ("cmd_left", [-1, 0], 1),
        ("cmd_down", [0, 1], 2),
        ("cmd_right", [1, 0], 3),
    ],
)
def test_direction_commands_set_the_expected_movement(command, expected_move, expected_image):
    ship = objship.Ship()

    getattr(ship, command)()

    # 每个方向命令应设置单一移动向量、对应朝向图像和已移动状态。
    assert ship.move == expected_move
    assert ship.image == expected_image
    assert ship.unmoved == 0


@pytest.mark.parametrize(
    ("start", "command", "expected_position"),
    [
        ((40, 0), "cmd_up", (40, 0)),
        ((40, 90), "cmd_down", (40, 90)),
        ((0, 40), "cmd_left", (0, 40)),
        ((90, 40), "cmd_right", (90, 40)),
    ],
)
def test_ship_cannot_move_beyond_arena_boundaries(start, command, expected_position):
    ship = objship.Ship()
    ship.start(start)

    getattr(ship, command)()
    ship.tick()

    # 越界移动会被裁剪到 arena 边界，同时清除该方向的移动命令。
    assert ship.rect.topleft == expected_position
    assert ship.move == [0, 0]


def test_shield_state_increases_ship_movement_speed():
    normal_ship = objship.Ship()
    normal_ship.start((10, 10))
    normal_ship.cmd_right()
    normal_ship.tick()

    shielded_ship = objship.Ship()
    shielded_ship.start((10, 10))
    shielded_ship.cmd_right()
    shielded_ship.shield = 1
    shielded_ship.tick()

    # 以相同初始位置和同一帧更新比较普通状态与护盾状态的位移。
    assert normal_ship.rect.left == 20
    assert shielded_ship.rect.left == 23
    assert shielded_ship.rect.left > normal_ship.rect.left


def test_fireball_moves_along_its_direction_vector():
    fireball = objshot.Shot((20, 20), (3, -2))

    fireball.tick(2)

    # 速度调整值会同时作用于火球的水平和垂直移动量。
    assert fireball.pos == [23, 13]
    assert fireball.rect.topleft == (23, 13)
    assert fireball.dead == 0


def test_fireball_is_marked_dead_after_leaving_the_display_area():
    fireball = objshot.Shot((98, 50), (10, 0))

    fireball.tick()

    assert fireball.dead == 1


def test_powerup_wraps_to_the_opposite_side_after_crossing_bounds(monkeypatch):
    image = pygame.Surface((20, 20))
    powerup = objpowerup.Powerup.__new__(objpowerup.Powerup)
    powerup.pos = [739.0, 639.0]
    powerup.speed = 2
    powerup.rect = image.get_rect()
    powerup.images = [image]
    powerup.time = 0
    powerup.dead = 0
    monkeypatch.setattr(game, "poweruptime", 100)

    # 源码使用模运算处理坐标，因此从右下边界越出后回到左上坐标范围。
    powerup.tick(1)

    assert powerup.pos == [1.0, 1.0]
    assert powerup.rect.topleft == (-19, -19)
    assert powerup.dead == 0
