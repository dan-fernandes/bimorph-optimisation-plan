from datetime import datetime

def generate_filename(file_prefix:str = None, file_timestamp_format:str = None):
    """Generated a filename (without path) for plan output csv

    Args:
        file_prefix (optional): Prefix for filename
        file_timestamp_format (optional): datetime library timestamp format for filename
    
    Returns:
        A string fiename without full path
    """
    filename = ""

    if file_prefix is not None:
        filename += file_prefix
    else:
        filename += "pencilbeam-data-"
    
    if file_timestamp_format is not  None:
        filename += datetime.now().strftime(file_timestamp_format)
    else:
        filename += datetime.now().strftime("%d-%m-%Y-%H-%M")
    
    filename += ".csv"

    return filename



