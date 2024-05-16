from argparse import ArgumentParser
import json

from . import __version__

__all__ = ["main"]


def main(args=None):
    parser = ArgumentParser()
    parser.add_argument("config_filepath", type=str, nargs=1, help="Filepath to configuration json")
    parser.add_argument("-v", "--version", action="version", version=__version__)
    args = parser.parse_args(args)

    with open(args.config_filepath[0]) as file:
        config_dict = json.load(file)
    

# test with: python -m bimorph_optimisation_plan
if __name__ == "__main__":
    main()
