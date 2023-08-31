import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp

from dodal.devices.bimorph_mirrors.CAENels_bimorph_mirror_interface import (
    ChannelAttribute,
)
from dodal.devices.oav.oav_detector import OAV


def voltage_list_generator(initial_list, increment):
    yield initial_list

    for i in range(len(initial_list)):
        initial_list[i] += increment

        yield initial_list


def slit_position_generator(
    slit_size, slit_centre_start, slit_centre_end, number_of_slit_positions
):
    slit_centre_increment = (
        slit_centre_start - slit_centre_end
    ) / number_of_slit_positions

    for i in range(number_of_slit_positions):
        yield slit_centre_increment * i, slit_size


# @bpp.run_decorator
# this wil be a stub:
def my_plan(bimorph, target_voltages):
    yield from bps.open_run()

    yield from bps.trigger_and_read(
        bimorph.get_channels_by_attribute(ChannelAttribute.VOUT_RBV)
    )

    yield from bps.close_run()


def get_centroids(
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

        for slit_position in slit_position_generator(
            slit_size, slit_centre_start, slit_centre_end, number_of_slit_positions
        ):
            yield from bps.read([slit])
            yield from bps.mv(slit, *slit_position)
            yield from bps.trigger_and_read([oav.stats.centroid])
    bps.close_run()

def get_centroids_2d(
    bimorph,
    slit,
    oav,
    initial_voltage_list,
    voltage_increment,
    x_slit_active_size,
    x_slit_centre_start,
    x_slit_centre_end,
    x_slit_dormant_size,
    x_number_of_slit_positions,
    y_slit_active_size,
    y_slit_centre_start,
    y_slit_centre_end,
    y_slit_dormant_size,
    y_number_of_slit_positions,
):

    bps.open_run()
    for voltage_list in voltage_list_generator(initial_voltage_list, voltage_increment):
        yield from bps.mv(bimorph, voltage_list)
        yield from bps.read(bimorph)

        for slit_position in slit_position_generator(
            x_slit_active_size, x_slit_centre_start, x_slit_centre_end, x_number_of_slit_positions
        ):
            yield from bps.read([slit])
            yield from bps.mv(slit, *slit_position)
            yield from bps.trigger_and_read([oav.stats.centroid])
        
        for slit_position in slit_position_generator(
            y_slit_active_size, y_slit_centre_start, y_slit_centre_end, y_number_of_slit_positions
        ):
            
        
    bps.close_run()

def oav_plan(oav: OAV):
    yield from bps.open_run()

    yield from bps.trigger_and_read([oav.stats.centroid])

    yield from bps.close_run()
