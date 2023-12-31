import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp

from dodal.devices.bimorph_mirrors.CAENels_bimorph_mirror_interface import (
    ChannelAttribute,
)
from dodal.devices.oav.oav_detector import OAV

from ophyd import Component, Device, EpicsSignalRO

from enum import Enum


class CentroidDevice(Device):
    centroid_x_rbv: EpicsSignalRO = Component(
        EpicsSignalRO, "-DI-OAV-01:STAT:CentroidX_RBV"
    )
    centroid_y_rbv: EpicsSignalRO = Component(
        EpicsSignalRO, "-DI-OAV-01:STAT:CentroidY_RBV"
    )


def voltage_list_generator(initial_list, increment):
    yield initial_list

    for i in range(len(initial_list)):
        initial_list[i] += increment

        yield initial_list


def slit_position_generator_1d(
    slit_size, slit_centre_start, slit_centre_end, number_of_slit_positions
):
    slit_centre_increment = (
        slit_centre_end - slit_centre_start
    ) / number_of_slit_positions

    for i in range(number_of_slit_positions):
        yield (slit_centre_increment * i + slit_centre_start, slit_size)


"""
def get_centroids_1d(
    bimorph,
    slit,
    oav,
    initial_voltage_list,
    voltage_increment,
    slit_size,
    slit_centre_start,
    slit_centre_end,
    number_of_slit_positions,
):
    bps.open_run()
    for voltage_list in voltage_list_generator(initial_voltage_list, voltage_increment):
        yield from bps.mv(bimorph, voltage_list)
        yield from bps.read(bimorph)

        for slit_position in slit_position_generator_1d(
            slit_size, slit_centre_start, slit_centre_end, number_of_slit_positions
        ):
            yield from bps.mv(slit, *slit_position)
            yield from bps.read([slit])
            yield from bps.trigger_and_read([oav.stats.centroid])

    bps.close_run()
"""


def get_centroids_2d(
    bimorph,
    slit,
    x_oav,
    y_oav,
    initial_voltage_list,
    voltage_increment,
    x_slit_active_size,
    x_slit_centre_start,
    x_slit_centre_end,
    x_number_of_slit_positions,
    x_slit_dormant_size,
    x_slit_dormant_centre,
    y_slit_active_size,
    y_slit_centre_start,
    y_slit_centre_end,
    y_number_of_slit_positions,
    y_slit_dormant_size,
    y_slit_dormant_centre,
):
    def take_readings(oav):
        centroid_device = CentroidDevice(
            name=f"{oav.prefix}_centroid_device", prefix=oav.prefix
        )
        yield from bps.create()

        for signal in bimorph.get_channels_by_attribute(ChannelAttribute.VOUT_RBV):
            yield from bps.read(signal)

        for signal in (slit.x_size, slit.x_centre, slit.y_size, slit.y_centre):
            yield from bps.read(signal)

        yield from bps.stage(oav)
        yield from bps.trigger(oav)
        yield from bps.read(centroid_device)
        yield from bps.unstage(oav)

        yield from bps.save()

    yield from bps.open_run()

    for voltage_list in voltage_list_generator(initial_voltage_list, voltage_increment):
        yield from bps.mv(bimorph, voltage_list)

        """

        for x_position in slit_position_generator_1d(
            x_slit_active_size, x_slit_centre_start, x_slit_centre_end, x_number_of_slit_positions
        ):
            slit_position = (*x_position, y_slit_dormant_centre, y_slit_dormant_size)
            yield from bps.mv(slit, slit_position)

            take_readings(x_oav)

        """

        for y_position in slit_position_generator_1d(
            y_slit_active_size,
            y_slit_centre_start,
            y_slit_centre_end,
            y_number_of_slit_positions,
        ):
            slit_position = (x_slit_dormant_centre, x_slit_dormant_size, *y_position)
            yield from bps.mv(slit, slit_position)

            take_readings(y_oav)

    yield from bps.close_run()
