from enum import Enum

import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
from dodal.devices.bimorph_mirrors.CAENels_bimorph_mirror_interface import (
    CAENelsBimorphMirrorInterface,
    ChannelAttribute,
)
from dodal.devices.slits.gap_and_centre_slit_base_classes import GapAndCentreSlit2d
from ophyd import Component, Device, EpicsSignalRO


class SlitDimension(Enum):
    """Enum representing the dimensions of a 2d slit

    Used to describe which dimension the pencil beam scan should move across.
    The other dimension will be held constant.

    Attributes:
        X: Represents X dimension
        Y: Represents Y dimension
    """
    X = "X",
    Y = "Y"


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


def slit_position_generator_2d(
    active_slit_centre_start: float,
    active_slit_centre_end: float,
    active_slit_size: float,
    dormant_slit_centre: float,
    dormant_slit_size: float,
    number_of_slit_positions: int,
    slit_dimension: SlitDimension,
):

    """Generator that yields positions to write to a 2d slit for a pencil beam scan.

    Yields positions that vary across one dimension, while keeping the other constant.
    
    Args:
        active_slit_centre_start: start position of centre of slit in active dimension
        active_slit_centre_end: final position of centre of slit in active dimension
        active_slit_size: size of slit in active dimension
        dormant_slit_centre: centre of slit in inactive dimension
        dormant_slit_size: size of slit in inactive dimension
        number_of_slit_positions: number of slit positions generated
        slit_dimension: active dimension (X or Y)
    
    Yield:
        A position to write to slit in form  (x_centre, x_size, y_centre, y_size)
    """
    active_slit_centre_increment = (
        active_slit_centre_end - active_slit_centre_start
    ) / number_of_slit_positions

    for i in range(number_of_slit_positions):
        active_slit_center = slit_centre_increment * i + active_slit_centre_start
        if SlitDimension == SlitDimension.X:
            yield (active_slit_center, active_slit_size, dormant_slit_centre, dormant_slit_size)
        else:
            yield(dormant_slit_centre, dormant_slit_size, active_slit_center, active_slit_size)



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
        A position to write to slit in form (Center, Size)
    """

    slit_centre_increment = (
        slit_centre_end - slit_centre_start
    ) / number_of_slit_positions

    for i in range(number_of_slit_positions):
        yield (slit_centre_increment * i + slit_centre_start, slit_size)


def pencil_beam_scan_2d_slit(
    bimorph: CAENelsBimorphMirrorInterface,
    slit: GapAndCentreSlit2d,
    centroid_device: CentroidDevice,
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
    bimorph_settle_time: float,
    initial_voltage_list: list = None,
):
    """Bluesky plan that performs a pencil beam scan across one axis using a 2-dimensional slit.

    Performs a pencil beam scan across one axis, keeping the size and position of the complimentary axis constant.
    """
    def take_readings():
        yield from bps.create()

        for signal in bimorph.get_channels_by_attribute(ChannelAttribute.VOUT_RBV):
            yield from bps.read(signal)

        for signal in (slit.x_size, slit.x_centre, slit.y_size, slit.y_centre):
            yield from bps.read(signal)

        yield from bps.read(centroid_device)

        yield from bps.save()

    yield from bps.open_run()

    start_voltages = bimorph.read_from_all_channels_by_attribute(ChannelAttribute.VOUT_RBV)

    # By default, if no initial voltages supplied, use current voltages as start:
    if initial_voltage_list is None:
        initial_voltage_list = start_voltages
    slit_read = slit.read()
    start_slit_positions = [
        slit_read[0]["slit_x_centre_readback_value"]["value"],
        slit_read[1]["slit_x_size_readback_value"]["value"],
        slit_read[2]["slit_y_centre_readback_value"]["value"],
        slit_read[3]["slit_y_size_readback_value"]["value"],
    ]
    print(f"start_slit_positions: {start_slit_positions}")

    bimorph_move_count = 1
    for voltage_list in voltage_list_generator(initial_voltage_list, voltage_increment):
        print(f"Applying volts: {voltage_list}")
        yield from bps.mv(bimorph, voltage_list, settle_time=bimorph_settle_time)
        print("Settling...")

        slit_dimension = SlitDimension.Y

        """

        for x_position in slit_position_generator_1d(
            x_slit_active_size, x_slit_centre_start, x_slit_centre_end, x_number_of_slit_positions
        ):
            slit_position = (*x_position, y_slit_dormant_centre, y_slit_dormant_size)
            yield from bps.mv(slit, slit_position)

            take_readings(x_oav)

        """
        slit_move_count = 1
        if slit_dimension == SlitDimension.Y:
            for y_position in slit_position_generator_1d(
                y_slit_active_size,
                y_slit_centre_start,
                y_slit_centre_end,
                y_number_of_slit_positions,
            ):
                print(
                    f"Bimorph position: {voltage_list} ({bimorph_move_count}/{len(initial_voltage_list)+1}), Slit position Center: {y_position[0]} Size: {y_position[1]} ({slit_move_count}/{y_number_of_slit_positions})"
                )
                slit_position = (
                    x_slit_dormant_centre,
                    x_slit_dormant_size,
                    *y_position,
                )
                yield from bps.mv(slit, slit_position)

                yield from take_readings()

                slit_move_count += 1

        else:
            for x_position in slit_position_generator_1d(
                x_slit_active_size,
                x_slit_centre_start,
                x_slit_centre_end,
                x_number_of_slit_positions,
            ):
                print(
                    f"Bimorph position: {voltage_list} ({bimorph_move_count}/{len(initial_voltage_list)}+1), Slit position Center: {x_position[0]} Size: {x_position[1]} ({slit_move_count}/{x_number_of_slit_positions})"
                )
                slit_position = (
                    *x_position,
                    y_slit_dormant_centre,
                    y_slit_dormant_size,
                )
                yield from bps.mv(slit, slit_position)

                yield from take_readings()

                slit_move_count += 1
        bimorph_move_count += 1

    print(f"Moving bimorph to original position {start_voltages}...")
    yield from bps.mv(bimorph, start_voltages)
    print(f"Moving slits to original position {start_slit_positions}...")
    yield from bps.mv(slit, start_slit_positions)

    print("Complete.")
    yield from bps.close_run()
