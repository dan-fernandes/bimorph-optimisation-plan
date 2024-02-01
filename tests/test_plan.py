import random

from bluesky import RunEngine
from bluesky.callbacks import LiveTable

# from bluesky.callbacks.best_effort import BestEffortCallback

from dodal.devices.bimorph_mirrors.CAENels_bimorph_mirror_7_channel import (
    CAENelsBimorphMirror7Channel,
)
from dodal.devices.bimorph_mirrors.CAENels_bimorph_mirror_8_channel import (
    CAENelsBimorphMirror8Channel,
)
from dodal.devices.bimorph_mirrors.CAENels_bimorph_mirror_16_channel import (
    CAENelsBimorphMirror16Channel,
)
from dodal.devices.oav.oav_detector import OAV

# from dodal.devices.slits.S5_BL02J_AL_SLITS_95 import S5_BL02J_AL_SLITS_95 as Slit
from dodal.devices.slits.i24_slits_04_virtual_motors import (
    I24Slits04VirtualMotors as Slit,
)

# from dodal.devices.slits.I24_SLITS_04_VIRTUAL_MOTORS import (
#    I24_SLITS_04_VIRTUAL_MOTORS as Slit,
# )

from bimorph_optimisation_plan.plan import pencil_beam_scan_2d_slit

import pytest

RE = RunEngine({})
# bec = BestEffortCallback()
# RE.subscribe(bec)
BIMORPH_PREFIX = "BL02J-EA-IOC-97:G0:"
# BIMORPH_PREFIX = "BL24I-OP-PFM-01:G1:"
SLIT_PREFIX = "BL02J-AL-SLITS-95:"
# SLIT_PREFIX = "BL24I-AL-SLITS-02:"
OAV_PREFIX = "BL24I"
"""
"initial_voltage_list": [
    -118.0,
    -125.0,
    -179.0,
    -202.0,
    -194.0,
    -242.0,
    -227.0,
    -195.0,
    -231.0,
    -282.0,
    -172.0,
    -188.0,
    -137.0,
    -51.0,
    1.0,
    -69.0,
],
"""

CONFIG = {
    # "initial_voltage_list": [-145.0, -82.0, -76.0, -29.0 - 3.0, 54.0, 121.0],
    "initial_voltage_list": [
        -168.0,
        -175.0,
        -229.0,
        -252.0,
        -244.0,
        -292.0,
        -277.0,
        -245.0,
        -281.0,
        -332.0,
        -222.0,
        -238.0,
        -187.0,
        -101.0,
        -49.0,
        -119.0,
    ],
    "voltage_increment": 200,
    "x_slit_size": 0.025,
    "x_slit_centre_start": -11.5,
    "x_slit_centre_end": 24.5,
    "x_number_of_slit_positions": 240,  # 180,
    "x_slit_dormant_centre": 5.5,
    "x_slit_dormant_size": 3.0,
    "y_slit_size": 0.007,
    "y_slit_centre_start": 1.82,
    "y_slit_centre_end": 2.220,
    "y_number_of_slit_positions": 40,  # 240,
    "y_slit_dormant_centre": 2.33,
    "y_slit_dormant_size": 3.0,
    "camera_exposure": 0.04,
    "bimorph_settle_time": 30,
    "output_file_path": "/home/fiw35684/temp/bimorph_test_output.csv",
}


def get_bimorph(bimorph_prefix=BIMORPH_PREFIX):
    # bimorph = CAENelsBimorphMirror7Channel(name="bimorph", prefix=bimorph_prefix)
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


def make_csv(docs):
    csv_dict = {}
    headers = []

    for doc in docs:
        if "run_start" in doc and "data_keys" in doc:
            headers = [header for header in doc["data_keys"]]
            headers.sort()
            for header in headers:
                csv_dict[header] = []

        elif "descriptor" in doc:
            for header in doc["data"]:
                csv_dict[header].append(str(doc["data"][header]))

    csv_str = ",".join(headers) + "\n"

    # print([row for row in zip(*[csv_dict[header] for header in headers])])

    csv_str += "\n".join(
        [",".join(row) for row in zip(*[csv_dict[header] for header in headers])]
    )

    # return csv_str
    return csv_str


# @pytest.mark.foo
def test_pencil_beam_scan_2d_slit(config=CONFIG):
    bimorph = get_bimorph()
    bimorph.settle_time = config["bimorph_settle_time"]
    slit = get_slit()
    oav = get_oav()
    import json

    def dump_docs(_, doc):
        breakpoint()
        print(json.dumps(doc))
        print("\nfoo\n")

    my_list = []

    def aggregate_docs(_, doc):
        my_list.append(doc)

    RE(
        pencil_beam_scan_2d_slit(
            bimorph,
            slit,
            oav,
            oav,
            config["initial_voltage_list"],
            config["voltage_increment"],
            config["x_slit_size"],
            config["x_slit_centre_start"],
            config["x_slit_centre_end"],
            config["x_number_of_slit_positions"],
            config["x_slit_dormant_size"],
            config["x_slit_dormant_centre"],
            config["y_slit_size"],
            config["y_slit_centre_start"],
            config["y_slit_centre_end"],
            config["y_number_of_slit_positions"],
            config["y_slit_dormant_size"],
            config["y_slit_dormant_centre"],
        ),
        aggregate_docs,
    )

    csv = make_csv(my_list)
    print(csv)
    with open(config["output_file_path"], "w") as file:
        file.write(csv)


# @pytest.mark.foo
def test_reads():
    bimorph = get_bimorph()
    slit = get_slit()
    import json

    def dump_docs(_, doc):
        print(json.dumps(doc))

    import bluesky.plan_stubs as bps
    from dodal.devices.bimorph_mirrors.CAENels_bimorph_mirror_interface import (
        ChannelAttribute,
    )

    def read_bimorph_slit_plan(bimorph, slit):
        bps.open_run()
        bps.create()
        for signal in bimorph.get_channels_by_attribute(ChannelAttribute.VOUT_RBV):
            a = yield from bps.read(signal)
            print(a)

        for signal in (slit.x_size, slit.x_centre, slit.y_size, slit.y_centre):
            a = yield from bps.read(signal)
            print(a)
        bps.save()
        bps.close_run()

    RE(read_bimorph_slit_plan(bimorph, slit), dump_docs)
