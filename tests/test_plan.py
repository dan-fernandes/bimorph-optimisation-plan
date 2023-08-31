import random

from bluesky import RunEngine
from bluesky.callbacks import LiveTable

# from bluesky.callbacks.best_effort import BestEffortCallback

from dodal.devices.bimorph_mirrors.CAENels_bimorph_mirror_8_channel import (
    CAENelsBimorphMirror8Channel,
)
from dodal.devices.oav.oav_detector import OAV
from dodal.devices.slits.S5_BL02J_AL_SLITS_95 import S5_BL02J_AL_SLITS_95 as Slit

from bimorph_optimisation_plan.plan import get_centroids_1d

RE = RunEngine({})
# bec = BestEffortCallback()
# RE.subscribe(bec)
BIMORPH_PREFIX = "BL02J-EA-IOC-97:G0:"
SLIT_PREFIX = "BL02J-AL-SLITS-95:"
OAV_PREFIX = "BL24I"

CONFIG = {
    "initial_voltage_list": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    "voltage_increment": 200,
    "slit_size": 1,
    "slit_centre_start": 0,
    "slit_centre_end": 10,
    "number_of_slit_positions": 10,
    "camera_exposure": 1,
    "bimorph_settle_time": 600,
}


def get_bimorph(bimorph_prefix=BIMORPH_PREFIX):
    bimorph = CAENelsBimorphMirror8Channel(name="bimorph", prefix=bimorph_prefix)
    bimorph.wait_for_connection()
    return bimorph


def get_slit(slit_prefix=SLIT_PREFIX):
    slit = Slit(name="slit", prefix=slit_prefix)
    slit.wait_for_connection()
    return slit


def get_oav(oav_prefix=OAV_PREFIX):
    oav = OAV(name="oav", prefix=oav_prefix)
    oav.wait_for_connection()
    return oav


def test_get_centroids_1d(config=CONFIG):
    bimorph = get_bimorph()
    slit = get_slit()
    oav = get_oav()

    RE(
        get_centroids_1d(
            bimorph,
            slit,
            oav,
            config["initial_voltage_list"],
            config["voltage_increment"],
            config["slit_size"],
            config["slit_centre_start"],
            config["slit_centre_end"],
            config["number_of_slit_positions"],
        ),
        print,
    )
