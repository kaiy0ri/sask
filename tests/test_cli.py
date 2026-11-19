import pytest

from sask import __version__
from sask.cli import COMMANDS, main


def test_version(capsys):
    with pytest.raises(SystemExit) as e:
        main(["--version"])
    assert e.value.code == 0
    assert __version__ in capsys.readouterr().out


@pytest.mark.parametrize("name", sorted(COMMANDS))
def test_stub_exits_nonzero(name, capsys):
    arg = COMMANDS[name][1]
    argv = [name, "x"] if arg else [name]
    assert main(argv) == 1
    assert "not implemented" in capsys.readouterr().err
