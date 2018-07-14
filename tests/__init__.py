from io import StringIO
from pathlib import Path

from pytest import fixture

from drawing import (
    DEFAULT_POINT_VALUE,
    CanvasCommandProcessor,
    Coord,
    canvas_to_out,
)


@fixture()
def processor():
    yield CanvasCommandProcessor()


def test_crate_canvas(processor):
    canvas = processor.process('C 3 2')

    assert canvas.size == Coord(3, 2)
    assert canvas.square == [
        [DEFAULT_POINT_VALUE, DEFAULT_POINT_VALUE],
        [DEFAULT_POINT_VALUE, DEFAULT_POINT_VALUE],
        [DEFAULT_POINT_VALUE, DEFAULT_POINT_VALUE],
    ]


def test_integration(processor):
    out = StringIO()
    current_dir = Path(__file__).parent

    with open(current_dir / 'input.txt', 'r') as f:
        for command in f:
            canvas = processor.process(command.rstrip('\n'))
            canvas_to_out(canvas, out)

    with open(current_dir / 'output.txt', 'r') as f:
        assert out.getvalue() == f.read()
