import contextlib
import io
import logging
import os
import tempfile

import pytest
from machine import simulation
from translator import translator


@pytest.mark.golden_test("../golden/*.yml")
def test_translator_and_machine(golden, caplog):
    caplog.set_level(logging.INFO)

    with tempfile.TemporaryDirectory() as tmp_dir_name:
        source = os.path.join(tmp_dir_name, "code")
        out_bin = os.path.join(tmp_dir_name, "out.bin")
        input_stream = os.path.join(tmp_dir_name, "input")
        debug = os.path.join(tmp_dir_name, "debug")

        with open(source, "w", encoding="utf-8") as file:
            file.write(golden["in_source"])
        with open(input_stream, "w", encoding="utf-8") as file:
            file.write(golden["in_stdin"])
            
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            translator.main(source, out_bin, debug)
            simulation.main(out_bin, input_stream)

        with open(debug, encoding="utf-8") as file:
            log = file.read()

        assert log == golden.out["translator_log"]
        assert stdout.getvalue() == golden.out["out_stdout"]
        assert caplog.text == golden.out["machine_log"]
