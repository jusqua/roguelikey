from engine import Engine
from input_handling import MainGameEventHandler
from project import save_game, load_game, new_game, save_file_name


def test_new_game():
    assert isinstance(new_game(), Engine)


def test_save_game():
    handler = MainGameEventHandler(new_game())
    save_game(handler, save_file_name)


def test_load_game():
    assert isinstance(load_game(save_file_name), Engine)
