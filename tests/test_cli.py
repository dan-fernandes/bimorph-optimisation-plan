import subprocess
import sys

from bimorph_optimisation_plan import __version__


def test_cli_version():
    cmd = [sys.executable, "-m", "bimorph_optimisation_plan", "--version"]
    assert subprocess.check_output(cmd).decode().strip() == __version__
