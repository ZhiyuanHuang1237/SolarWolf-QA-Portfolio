"""SolarWolf 白盒自动化：存档对象、保存读取与槽位独立性。"""

import sys
from pathlib import Path

import pytest


# 被测游戏源码路径；测试代码自身仍位于 QA 作品集目录中。
GAME_SOURCE = Path(__file__).resolve().parents[2] / "solarwolf" / "solarwolf"
if str(GAME_SOURCE) not in sys.path:
    sys.path.insert(0, str(GAME_SOURCE))

import game  # noqa: E402
import players  # noqa: E402


@pytest.fixture
def isolated_player_store(tmp_path, monkeypatch):
    """将玩家数据读写重定向至 pytest 临时目录，绝不触碰真实存档。"""
    data_file = tmp_path / "players"
    previous_players = players.players
    previous_winners = players.winners
    # 备份模块级列表，并使用空列表隔离本次测试数据。
    players.players = []
    players.winners = []
    monkeypatch.setattr(game, "make_dataname", lambda name: str(data_file))
    yield
    players.players = previous_players
    players.winners = previous_winners


def test_same_name_players_receive_different_save_identifiers():
    player_a = players.Player("Test Player")
    player_b = players.Player("Test Player")

    # 名称可以相同，但 guid 才是区分两个独立存档的标识。
    assert player_a.name == player_b.name
    assert player_a.guid != player_b.guid


def test_save_and_load_preserve_independent_same_name_slots(isolated_player_store):
    player_a = players.Player("Test Player", guid="test-slot-a", score=3)
    player_b = players.Player("Test Player", guid="test-slot-b", score=3)
    player_a.lives = 4
    player_b.lives = 1
    players.players = [player_a, player_b]

    # 两个同名、同分数的存档刻意设置不同 lives 值，用于验证隔离性。
    players.save_players()
    players.players = []
    players.winners = []
    players.load_players()

    # 重新读取临时文件后，按各自 guid 检索，而非按相同名称检索。
    loaded_a = players.find_player("test-slot-a")
    loaded_b = players.find_player("test-slot-b")
    assert loaded_a is not None
    assert loaded_b is not None
    assert loaded_a.name == loaded_b.name == "Test Player"
    assert loaded_a.score == loaded_b.score == 3
    assert loaded_a.lives == 4
    assert loaded_b.lives == 1


@pytest.mark.parametrize(
    ("score", "expected_start_level"),
    [(-1, 0), (0, 0), (1, 1), (12, 12)],
)
def test_start_level_is_derived_from_saved_progress(score, expected_start_level):
    player = players.Player("Test Player", guid="test-slot", score=score)

    # score 为 0 或负数时从初始关开始；正数保留为可继续的起始关卡。
    assert player.start_level() == expected_start_level
