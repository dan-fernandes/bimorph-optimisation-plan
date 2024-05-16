from argparse import ArgumentParser
from bluesky import RunEngine
import device_instantiator
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
    

def run_plan(config_dict):
    RE = RunEngine({})

    bimorph = device_instantiator.get_bimorph(
        config.get("bimorph_type"),
        config.get("bimorph_prefix"),
        config.get("bimorph_name")
    )

    slit = device_instantiator.get_slit(
        config.get("slit_type"),
        config.get("slit_prefix"),
        config.get("slit_name")
    )

    oav = device_instantiator.get_oav(
        config.get("oav_zoom_parameters_filepath"),
        config.get("oav_display_configuration_filepath"),
        config.get("oav_prefix"),
        config.get("oav_name")
    )



# test with: python -m bimorph_optimisation_plan
if __name__ == "__main__":
    main()
