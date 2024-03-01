import logging
import struct
import sys

from controlunit import ControlUnit


def main(source, target):
    commands = []
    with open(source, mode="rb") as f:
        for chunk in iter(lambda: f.read(4), ""):
            if chunk == b"":
                break
            integer_value = struct.unpack(">I", chunk)[0]
            integer_value = struct.pack(">I", integer_value)
            commands.append(integer_value)
    cu = ControlUnit(commands, 100000, target)
    cu.start_processering()


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    assert len(sys.argv) == 3, "Wrong arguments: simpulation.py <input_file> <target_file>"
    _, source, target = sys.argv
    main(source, target)
