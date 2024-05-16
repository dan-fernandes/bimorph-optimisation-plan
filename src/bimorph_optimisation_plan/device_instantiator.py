def get_bimorph(bimorph_type: str, bimorph_prefix: str, bimorph_name: str):
    """
    Takes config data and returns bimorph object of correct type.

    Args:
        bimorph_type: Type of bimorph to instantiate
        bimorph_prefix: Prefix for bimorph ophyd object
        bimorph_name: Name for bimorph ophyd object
    
    Returns:
        A bimorph ophyd object
    """
    if bimorph_type == "CAENelsBimorphMirror7Channel":
        from dodal.devices.bimorph_mirrors.CAENels_bimorph_mirror_7_channel import (
    CAENelsBimorphMirror7Channel)
        bimorph_class = CAENelsBimorphMirror7Channel
    
    bimorph = bimorph_class(name=bimorph_name, prefix=bimorph_prefix)
    bimorph.wait_for_connection()

    return bimorph

def get_slit(config_dict: dict):
    """
    Takes config data and returns slit object of correct type.

    Args:
        config_dict: dictionary containing slit_type and slit_prefix fields
    
    Returns:
        A slit ophyd object
    """    
    slit_type = config_dict["slit_type"]

    if slit_type == "I24Slits04VirtualMotors":
        from dodal.devices.slits.i24_slits_04_virtual_motors import (
    I24Slits04VirtualMotors)
        slit_class = I24Slits04VirtualMotors
    
    slit = slit_class(name="slit", prefix=config_dict["slit_prefix"])
    slit.wait_for_connection()

    return slit

def get_oav(config_dict: dict):
    """
    Takes config data and returns oav object of correct type.

    Args:
        config_dict: dictionary containing fields:
            oav_zoom_parameters_filepath
            oav_display_configuration_filepath
            oav_prefix

    Returns:
        An oav ophyd object
    """  
    from dodal.devices.oav.oav_detector import OAV, OAVConfigParams
    oav_config_params = OAVConfigParams(
        config_dict["oav_zoom_parameters_filepath"],
        config_dict["oav_display_configuration_filepath"],
    )

    oav = OAV(params = oav_config_params, name="oav", prefix=config_dict["oav_prefix"])
    oav.wait_for_connection()

    return oav
