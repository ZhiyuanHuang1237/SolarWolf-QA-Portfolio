"""SolarWolf 白盒自动化：小方块、特殊道具与火球交互逻辑。"""

import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
GAME_SOURCE = Path(__file__).resolve().parents[2] / "solarwolf" / "solarwolf"
if str(GAME_SOURCE) not in sys.path:
    sys.path.insert(0, str(GAME_SOURCE))

import pygame  # noqa: E402
import game  # noqa: E402
import objbox  # noqa: E402
import objpowerup  # noqa: E402
import gameplay  # noqa: E402


@pytest.fixture(autouse=True)
def initialise_pygame():
    pygame.init()


def make_yellow_box():
    box = objbox.Box.__new__(objbox.Box)
    box.rect = pygame.Rect(10, 10, 20, 20)
    box.touches = 2
    box.touching = 0
    box.firsttouch = 2.0
    return box


def make_normal_play_state(player, powerup, shots=None):
    """Build the state required by GamePlay.normal_tick for one interaction frame."""
    state = gameplay.GamePlay.__new__(gameplay.GamePlay)
    state.speedadjust = 1.0
    state.player = player
    state.powerupcount = 0.0
    state.guardobjs = []
    # A remaining box prevents this one-frame interaction test from ending a level.
    state.boxobjs = [SimpleNamespace(playercollide=lambda rect: 0)]
    state.powerupobjs = [powerup]
    state.grabbedboxes = 0
    state.numdeaths = 0
    state.complement = 0
    state.textobjs = []
    state.touchingsecretspike = None
    state.secretspikes = []
    state.shotobjs = shots or []
    state.spikeobjs = []
    state.asteroidobjs = []
    state.powereffects = []
    state.popobjs = []
    state.smokeobjs = []
    state.objlists = []
    state.tickleveltime = lambda speedadjust: None
    state.runobjects = lambda objects: None
    state.changestate = lambda name: None
    state.clocks = 0
    return state


def configure_powerup_collision(monkeypatch, effect_class, shots=None):
    """Prepare one normal-play frame where the ship overlaps a power-up."""
    player = SimpleNamespace(
        rect=pygame.Rect(10, 10, 12, 12),
        active=0,
        shield=0,
        turbo=0,
        move=[0, 0],
    )
    powerup = SimpleNamespace(
        rect=pygame.Rect(11, 11, 8, 8),
        dead=0,
        effect=effect_class,
    )
    state = make_normal_play_state(player, powerup, shots)
    monkeypatch.setattr(game, "handler", state)
    monkeypatch.setattr(game, "guard_fire", 0)
    monkeypatch.setattr(game, "powerupwait", 999999)
    monkeypatch.setattr(game, "comments", 0)
    monkeypatch.setattr(gameplay.gamehelp, "help", lambda *args, **kwargs: None)
    monkeypatch.setattr(objpowerup.snd, "play", lambda *args, **kwargs: None)
    return state, player, powerup


def test_yellow_box_requires_exit_before_second_valid_contact(monkeypatch):
    monkeypatch.setattr(objbox.snd, "play", lambda *args, **kwargs: None)
    box = make_yellow_box()
    player_inside = pygame.Rect(12, 12, 5, 5)
    player_outside = pygame.Rect(100, 100, 5, 5)

    # 第一次进入：剩余接触次数从 2 变为 1。
    assert box.playercollide(player_inside) == 2
    assert box.touches == 1

    # 玩家仍在同一碰撞框内时，不能重复计数。
    assert box.playercollide(player_inside) == 0
    assert box.touches == 1

    # 离开后重新进入，才构成第二次有效接触。
    assert box.playercollide(player_outside) == 0
    assert box.playercollide(player_inside) == 1
    assert box.touches == 0


def test_shot_blocker_marks_all_active_shots_for_removal(monkeypatch):
    monkeypatch.setattr(objpowerup.snd, "play", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        objpowerup.objpopshot,
        "PopShot",
        lambda center: ("pop", center),
    )
    shots = [
        SimpleNamespace(dead=0, rect=pygame.Rect(10, 10, 5, 5)),
        SimpleNamespace(dead=0, rect=pygame.Rect(20, 20, 5, 5)),
    ]
    state = SimpleNamespace(shotobjs=shots, popobjs=[])
    effect = objpowerup.PopShots.__new__(objpowerup.PopShots)
    effect.state = state

    effect.start()

    assert [shot.dead for shot in shots] == [1, 1]
    assert state.popobjs == [("pop", (12, 12)), ("pop", (22, 22))]


def test_shield_start_and_end_update_ship_shield_state(monkeypatch):
    monkeypatch.setattr(objpowerup.snd, "play", lambda *args, **kwargs: None)
    player = SimpleNamespace(shield=0)
    effect = objpowerup.Shield.__new__(objpowerup.Shield)
    effect.state = SimpleNamespace(player=player)

    effect.start()
    assert player.shield == 1

    effect.end()
    assert player.shield == 0


def make_normal_play_state(player, powerup, shots=None):
    state = gameplay.GamePlay.__new__(gameplay.GamePlay)
    state.speedadjust = 1.0
    state.player = player
    state.powerupcount = 0.0
    state.guardobjs = []
    state.boxobjs = [SimpleNamespace(playercollide=lambda rect: 0)]
    state.powerupobjs = [powerup]
    state.grabbedboxes = 0
    state.numdeaths = 0
    state.complement = 0
    state.textobjs = []
    state.touchingsecretspike = None
    state.secretspikes = []
    state.shotobjs = shots or []
    state.spikeobjs = []
    state.asteroidobjs = []
    state.powereffects = []
    state.popobjs = []
    state.smokeobjs = []
    state.objlists = []
    state.tickleveltime = lambda speedadjust: None
    state.runobjects = lambda objects: None
    state.changestate = lambda name: None
    state.clocks = 0
    return state


def configure_powerup_collision(monkeypatch, effect_class, shots=None):
    player = SimpleNamespace(
        rect=pygame.Rect(10, 10, 12, 12),
        active=0,
        shield=0,
        turbo=0,
        move=[0, 0],
    )
    powerup = SimpleNamespace(
        rect=pygame.Rect(11, 11, 8, 8),
        dead=0,
        effect=effect_class,
    )
    state = make_normal_play_state(player, powerup, shots)
    monkeypatch.setattr(game, "handler", state)
    monkeypatch.setattr(game, "guard_fire", 0)
    monkeypatch.setattr(game, "powerupwait", 999999)
    monkeypatch.setattr(game, "comments", 0)
    monkeypatch.setattr(gameplay.gamehelp, "help", lambda *args, **kwargs: None)
    monkeypatch.setattr(objpowerup.snd, "play", lambda *args, **kwargs: None)
    return state, player, powerup


def test_ship_collecting_shot_blocker_triggers_the_full_clear_shot_flow(monkeypatch):
    shots = [
        SimpleNamespace(dead=0, rect=pygame.Rect(80, 80, 5, 5)),
        SimpleNamespace(dead=0, rect=pygame.Rect(90, 90, 5, 5)),
    ]
    monkeypatch.setattr(
        objpowerup.objpopshot,
        "PopShot",
        lambda center: ("pop", center),
    )
    state, _, powerup = configure_powerup_collision(
        monkeypatch,
        objpowerup.PopShots,
        shots,
    )

    gameplay.GamePlay.normal_tick(state)

    assert powerup.dead == 1
    assert isinstance(state.powereffects[0], objpowerup.PopShots)
    assert [shot.dead for shot in shots] == [1, 1]


def test_ship_collecting_shield_triggers_the_shield_effect(monkeypatch):
    state, player, powerup = configure_powerup_collision(monkeypatch, objpowerup.Shield)

    gameplay.GamePlay.normal_tick(state)

    assert powerup.dead == 1
    assert isinstance(state.powereffects[0], objpowerup.Shield)
    assert player.shield == 1


def test_ship_collecting_clock_powerup_reverses_the_timer_tick(monkeypatch):
    monkeypatch.setattr(game, "timetick", 5)
    state, _, powerup = configure_powerup_collision(monkeypatch, objpowerup.ExtraLevelTime)

    gameplay.GamePlay.normal_tick(state)

    assert powerup.dead == 1
    assert isinstance(state.powereffects[0], objpowerup.ExtraLevelTime)
    assert game.timetick == -10


@pytest.mark.parametrize(
    ("guard_fire", "expected_fire_calls"),
    [(0.5, 1), (0.1, 0)],
)
def test_fire_request_uses_a_seeded_random_sequence(
    monkeypatch,
    guard_fire,
    expected_fire_calls,
):
    player = SimpleNamespace(
        rect=pygame.Rect(10, 10, 12, 12),
        active=1,
        shield=0,
        turbo=0,
        move=[0, 0],
    )
    placeholder_powerup = SimpleNamespace(
        rect=pygame.Rect(80, 80, 8, 8),
        dead=0,
        effect=objpowerup.Shield,
    )
    state = make_normal_play_state(player, placeholder_powerup)
    fire_calls = []
    guard = SimpleNamespace(
        fire=lambda: fire_calls.append("requested"),
        shotinfo=lambda: (None, None),
    )
    state.guardobjs = [guard]
    monkeypatch.setattr(game, "guard_fire", guard_fire)
    monkeypatch.setattr(game, "powerupwait", 999999)
    monkeypatch.setattr(game, "comments", 0)
    monkeypatch.setattr(gameplay.gamehelp, "help", lambda *args, **kwargs: None)
    monkeypatch.setattr(gameplay.random, "choice", lambda guards: guard)

    # 固定种子后，测试重复运行时会使用相同的第一组随机结果。
    gameplay.random.seed(2026)

    gameplay.GamePlay.normal_tick(state)

    assert len(fire_calls) == expected_fire_calls


def test_guard_shot_request_creates_a_fireball(monkeypatch):
    player = SimpleNamespace(
        rect=pygame.Rect(10, 10, 12, 12),
        active=0,
        shield=0,
        turbo=0,
        move=[0, 0],
    )
    placeholder_powerup = SimpleNamespace(
        rect=pygame.Rect(80, 80, 8, 8),
        dead=0,
        effect=objpowerup.Shield,
    )
    state = make_normal_play_state(player, placeholder_powerup)
    created = []

    def create_shot(position, direction):
        created.append((position, direction))
        return SimpleNamespace(dead=0, rect=pygame.Rect(80, 80, 5, 5))

    guard = SimpleNamespace(
        fire=lambda: None,
        shotinfo=lambda: ((70, 60), (1, 0)),
    )
    state.guardobjs = [guard]
    monkeypatch.setattr(game, "guard_fire", 0)
    monkeypatch.setattr(game, "powerupwait", 999999)
    monkeypatch.setattr(game, "comments", 0)
    monkeypatch.setattr(gameplay.gamehelp, "help", lambda *args, **kwargs: None)
    monkeypatch.setattr(gameplay.snd, "play", lambda *args, **kwargs: None)
    monkeypatch.setattr(gameplay.objshot, "Shot", create_shot)

    gameplay.GamePlay.normal_tick(state)

    assert created == [((70, 60), (1, 0))]
    assert len(state.shotobjs) == 1


def test_powerup_counter_threshold_generates_a_special_item(monkeypatch):
    player = SimpleNamespace(
        rect=pygame.Rect(10, 10, 12, 12),
        active=0,
        shield=0,
        turbo=0,
        move=[0, 0],
    )
    placeholder_powerup = SimpleNamespace(
        rect=pygame.Rect(80, 80, 8, 8),
        dead=0,
        effect=objpowerup.Shield,
    )
    state = make_normal_play_state(player, placeholder_powerup)
    state.powerupobjs = []
    state.powerupcount = 10
    state.levelnum = 7
    generated = SimpleNamespace(rect=pygame.Rect(80, 80, 8, 8), dead=0)
    requested_levels = []

    def create_powerup(level_number):
        requested_levels.append(level_number)
        return generated

    monkeypatch.setattr(game, "guard_fire", 0)
    monkeypatch.setattr(game, "powerupwait", 10)
    monkeypatch.setattr(game, "comments", 0)
    monkeypatch.setattr(gameplay.gamehelp, "help", lambda *args, **kwargs: None)
    monkeypatch.setattr(gameplay.snd, "play", lambda *args, **kwargs: None)
    monkeypatch.setattr(gameplay.objpowerup, "newpowerup", create_powerup)

    gameplay.GamePlay.normal_tick(state)

    assert requested_levels == [7]
    assert state.powerupcount == 0.0
    assert state.powerupobjs == [generated]


def test_ship_collecting_shot_blocker_triggers_the_full_clear_shot_flow(monkeypatch):
    shots = [
        SimpleNamespace(dead=0, rect=pygame.Rect(80, 80, 5, 5)),
        SimpleNamespace(dead=0, rect=pygame.Rect(90, 90, 5, 5)),
    ]
    monkeypatch.setattr(
        objpowerup.objpopshot,
        "PopShot",
        lambda center: ("pop", center),
    )
    state, _, powerup = configure_powerup_collision(
        monkeypatch,
        objpowerup.PopShots,
        shots,
    )

    gameplay.GamePlay.normal_tick(state)

    # Collision marks the collected item as dead, appends its effect, and clears shots.
    assert powerup.dead == 1
    assert isinstance(state.powereffects[0], objpowerup.PopShots)
    assert [shot.dead for shot in shots] == [1, 1]


def test_ship_collecting_shield_triggers_the_shield_effect(monkeypatch):
    state, player, powerup = configure_powerup_collision(monkeypatch, objpowerup.Shield)

    gameplay.GamePlay.normal_tick(state)

    assert powerup.dead == 1
    assert isinstance(state.powereffects[0], objpowerup.Shield)
    assert player.shield == 1


def test_ship_collecting_clock_powerup_reverses_the_timer_tick(monkeypatch):
    monkeypatch.setattr(game, "timetick", 5)
    state, _, powerup = configure_powerup_collision(monkeypatch, objpowerup.ExtraLevelTime)

    gameplay.GamePlay.normal_tick(state)

    assert powerup.dead == 1
    assert isinstance(state.powereffects[0], objpowerup.ExtraLevelTime)
    assert game.timetick == -10
