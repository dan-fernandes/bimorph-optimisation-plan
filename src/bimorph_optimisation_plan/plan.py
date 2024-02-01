import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp

from dodal.devices.bimorph_mirrors.CAENels_bimorph_mirror_interface import (
    ChannelAttribute,
)
from dodal.devices.slits.gap_and_centre_slit_base_classes import GapAndCentreSlit2d
from dodal.devices.oav.oav_detector import OAV

from ophyd import Component, Device, EpicsSignalRO

from enum import Enum


class CentroidDevice(Device):
    """Jank class to access the CentroidX_RBV of an oav detector.

    Attributes:
        centroid_x_rbv: An EpicsSignalRO for the centroid X readback value
        centroid_y_rbv: An EpicsSignalRO for the centroid Y readback value
    """
    centroid_x_rbv: EpicsSignalRO = Component(
        EpicsSignalRO, "-DI-OAV-01:STAT:CentroidX_RBV"
    )
    centroid_y_rbv: EpicsSignalRO = Component(
        EpicsSignalRO, "-DI-OAV-01:STAT:CentroidY_RBV"
    )


def voltage_list_generator(initial_list, increment):
    """Yields lists containing correct voltages to write to bimorph for pencil beam scan.

    The generator takes an initial list of voltages and an increment.
    It will apply this increment once to each element fron 0..n in turn.
    This is how a pencil scan applies voltages.
    
    Args:
        initial_list: the pre-increment list of voltages
        increment: float to increment each element by in turn
    
    Yields:
        A list of floats to apply to bimorph mirror
    """
    yield initial_list

    for i in range(len(initial_list)):
        initial_list[i] += increment

        yield initial_list


def slit_position_generator_1d(
    slit_size, slit_centre_start, slit_centre_end, number_of_slit_positions
):
    """Generator that yiels positions to write to slit for pencil beam scan.

    Args:
        slit_size: float constant gap size to write to slit
        slit_centre_start: float position of centre at start of scan
        slit_centre_end: float position of centre at end of scan
        number_of_slit_positions: integer number of moves slit will take to traverse scan
    
    Yields:
        A position to write to slit
    """

    slit_centre_increment = (
        slit_centre_end - slit_centre_start
    ) / number_of_slit_positions

    for i in range(number_of_slit_positions):
        yield (slit_centre_increment * i + slit_centre_start, slit_size)


def pencil_beam_scan_2d_slits(
    bimorph: CAENels_bimorph_mirror_interface,
    slit: GapAndCentreSlit2d,
    x_oav: OAV,
    y_oav: OAV,
    initial_voltage_list: list,
    voltage_increment: float,
    x_slit_active_size: float,
    x_slit_centre_start: float,
    x_slit_centre_end: float,
    x_number_of_slit_positions: int,
    x_slit_dormant_size: float,
    x_slit_dormant_centre: float,
    y_slit_active_size: float,
    y_slit_centre_start: float,
    y_slit_centre_end: float,
    y_number_of_slit_positions: int,
    y_slit_dormant_size: float,
    y_slit_dormant_centre: float,
):
    """Bluesky plan that performs a pencil beam scan across one axis using a 2-dimensional slit.

    Performs a pencil beam scan across one axis, keeping the size and position of the complimentary axis constant.
    """
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
