from digital_signatures import KeyLibrary
from transactions import (
    allocate_device_id,
    send_device_location,
    query_device_information,
)

from datetime import datetime


if __name__ == "__main__":
    result, id = allocate_device_id()
    print(result, id)

    sk = KeyLibrary.load_signing_key("priv_key.pem")

    print(send_device_location(id, "loc", sk))

    print(query_device_information(id))
