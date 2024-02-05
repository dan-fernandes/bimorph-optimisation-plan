import random

import pytest

# from dodal.devices.slits.I24_SLITS_04_VIRTUAL_MOTORS import (
#    I24_SLITS_04_VIRTUAL_MOTORS as Slit,
# )
from bimorph_optimisation_plan.plan import pencil_beam_scan_2d_slit
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
from dodal.devices.oav.oav_detector import OAV, OAVConfigParams

# from dodal.devices.slits.S5_BL02J_AL_SLITS_95 import S5_BL02J_AL_SLITS_95 as Slit
from dodal.devices.slits.i24_slits_04_virtual_motors import (
    I24Slits04VirtualMotors as Slit,
)

RE = RunEngine({})
# bec = BestEffortCallback()
# RE.subscribe(bec)
# BIMORPH_PREFIX = "BL02J-EA-IOC-97:G0:"
BIMORPH_PREFIX = "BL24I-OP-MFM-01:G0:"
# SLIT_PREFIX = "BL02J-AL-SLITS-95:"
SLIT_PREFIX = "BL24I-AL-SLITS-03:"
OAV_PREFIX = "BL24I"
ZOOM_PARAMS_FILE = "/dls_sw/i24/software/gda/config/xml/jCameraManZoomLevels.xml"   
DISPLAY_CONFIG = "/dls_sw/i24/software/gda_versions/var/display.configuration"

CONFIG = {
    "initial_voltage_list": [
        557.0,
        550.0,
        496.0,
        473.0,
        481.0,
        433.0,
        448.0,
        480.0,
        444.0,
        393.0,
        503.0,
        487.0,
        538.0,
        624.0,
        676.0,
        606.0,
    ],
    "voltage_increment": 100,  # 200,
    "x_slit_size": 0.01,
    "x_slit_centre_start": -11.5,
    "x_slit_centre_end": 24.5,
    "x_number_of_slit_positions": 1,  # 240,  # 180,
    "x_slit_dormant_centre": 1.94,
    "x_slit_dormant_size": 4.0,
    "y_slit_size": 0.007,
    "y_slit_centre_start": 1.5,
    "y_slit_centre_end": 2.3,
    "y_number_of_slit_positions": 16,  # 40,  # 240,
    "y_slit_dormant_centre": 5,
    "y_slit_dormant_size": 3.0,
    "camera_exposure": 0.04,
    "bimorph_settle_time": 0,  # 5,
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


def get_oav(oav_prefix=OAV_PREFIX, zoom_params_file=ZOOM_PARAMS_FILE, display_config=DISPLAY_CONFIG):
    oav_config_params = OAVConfigParams(zoom_params_file, display_config)
    oav = OAV(params = oav_config_params, name="oav", prefix=oav_prefix)
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

    csv_str += "\n".join(
        [",".join(row) for row in zip(*[csv_dict[header] for header in headers])]
    )

    # return csv_str
    return csv_str


# @pytest.mark.foo
def test_pencil_beam_scan_2d_slit(config=CONFIG):
    bimorph = get_bimorph()
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

    from bimorph_optimisation_plan.plan import CentroidDevice

    centroid_device = CentroidDevice(
        name=f"{OAV_PREFIX}_centroid_device", prefix=OAV_PREFIX
    )
    centroid_device.wait_for_connection()

    try:
        RE(
            pencil_beam_scan_2d_slit(
                bimorph,
                slit,
                centroid_device,
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
                config["bimorph_settle_time"],
            ),
            aggregate_docs,
        )
    finally:
        print("Saving data...")
        csv = make_csv(my_list)
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
