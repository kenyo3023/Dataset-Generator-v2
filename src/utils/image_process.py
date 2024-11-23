import base64
from typing import Literal

def encode_image(
    image_path:str,
    return_format:Literal['base64', 'decoded_base64', 'data_url']='data_url',
):
  with open(image_path, "rb") as image_file:

    data = base64.b64encode(image_file.read())
    if return_format == 'base64':
        return data

    data = data.decode('utf-8')
    if return_format == 'decoded_base64':
        return data

    data_url = f"data:image/jpeg;base64,{data}"
    return data_url