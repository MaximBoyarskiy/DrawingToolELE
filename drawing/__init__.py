import sys
from enum import Enum
from typing import (
    NamedTuple,
    Optional,
    TextIO,
)


DEFAULT_POINT_VALUE = " "


class Coord(NamedTuple):
    x: int
    y: int


class Command(Enum):
    create_canvas = "C"
    create_line = "L"
    create_rectangle = "R"
    bucket_fill = "B"


class Canvas:
    def __init__(self, coord: Coord) -> None:
        self.size = coord

        # square index starts from 0, however commands coordinates starts from 1;
        # We have to match it in get/set_point by reducing coordinate index by 1.
        self.square = [[DEFAULT_POINT_VALUE] * coord.y for _ in range(coord.x)]

    def get_point(self, coord: Coord) -> str:
        return self.square[coord.x - 1][coord.y - 1]

    def set_point(self, coord: Coord, value: str) -> None:
        self.square[coord.x - 1][coord.y - 1] = value


class CanvasCommandProcessor:
    canvas: Optional[Canvas] = None

    def process(self, command_raw: str) -> Canvas:
        command_name, *args = command_raw.strip().split(" ")
        command = Command(command_name)
        if command == Command.create_canvas:
            x, y = map(int, args)
            self.create_canvas(Coord(x, y))
        elif command == Command.create_line:
            x1, y1, x2, y2 = map(int, args)
            assert x1 == x2 or y1 == y2
            self.create_line(Coord(x1, y1), Coord(x2, y2))
        elif command == Command.create_rectangle:
            x1, y1, x2, y2 = map(int, args)
            self.create_rectangle(Coord(x1, y1), Coord(x2, y2))
        elif command == Command.bucket_fill:
            x_, y_, value = args
            x, y = map(int, (x_, y_,))
            self.bucket_fill(Coord(x, y), value)
        else:
            raise ValueError("Command could not be processed. Command %s", command)

        assert self.canvas is not None
        return self.canvas

    def create_canvas(self, coord: Coord) -> None:
        self.canvas = Canvas(coord)

    def create_line(self, start: Coord, end: Coord) -> None:
        assert self.canvas is not None

        if start.x == end.x:
            y_start, y_end = sorted((start.y, end.y,))
            for y in range(y_start, y_end + 1):
                self.canvas.set_point(Coord(start.x, y), "x")
        else:
            x_start, x_end = sorted((start.x, end.x,))
            for x in range(x_start, x_end + 1):
                self.canvas.set_point(Coord(x, start.y), "x")

    def create_rectangle(self, vertex1: Coord, vertex2: Coord):
        assert self.canvas is not None

        for start, end in (
            (vertex1, Coord(vertex2.x, vertex1.y),),
            (Coord(vertex2.x, vertex1.y), vertex2,),
            (vertex2, Coord(vertex1.x, vertex2.y),),
            (Coord(vertex1.x, vertex2.y), vertex1,),
        ):
            self.create_line(start, end)

    def bucket_fill(self, coord: Coord, new_value: str, old_value: Optional[str] = None) -> None:
        assert self.canvas is not None

        # old value is none means that it is an initial request.
        # In other case - recursion request to process neighbors.
        if old_value is None:
            old_value = self.canvas.get_point(coord)
            self.canvas.set_point(coord, new_value)
        else:
            if self.canvas.get_point(coord) != old_value:
                return

            self.canvas.set_point(coord, new_value)

        for neighbor_coord in (
            coord._replace(x=coord.x - 1),
            coord._replace(x=coord.x + 1),
            coord._replace(y=coord.y - 1),
            coord._replace(y=coord.y + 1),
        ):
            if (
                neighbor_coord.x in range(1, self.canvas.size.x + 1)
            ) and (
                neighbor_coord.y in range(1, self.canvas.size.y + 1)
            ):
                self.bucket_fill(neighbor_coord, new_value, old_value)


def canvas_to_out(canvas: Canvas, out: TextIO) -> None:
    size = canvas.size
    print("-" * (size.x + 2), file=out,)

    # We could use numpy to transpose list and print it in more efficient way
    for y in range(1, size.y + 1):
        line = ""
        line += "|"
        for x in range(1, size.x + 1):
            line += canvas.get_point(Coord(x, y))
        line += "|"
        print(line, file=out)

    print("-" * (size.x + 2), file=out)


def main() -> int:
    processor = CanvasCommandProcessor()
    try:
        while True:
            canvas = processor.process(sys.stdin.readline())
            canvas_to_out(canvas, sys.stdout)
    except KeyboardInterrupt:
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
