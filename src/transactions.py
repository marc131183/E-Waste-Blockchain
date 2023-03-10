"""
The following transaction types exist:

    BLOCK:
        This transaction type records the transfer of an item to a new place and has the following format:
        BLOCK=DEVICE-ID=LOCATION=TIMESTAMP=SIGNED-DIGEST

        Explanation of attributes:
        BLOCK:                  identifier that this transaction is of the type BLOCK
        DEVICE-ID:              device id
        LOCATION:               name of the site that the item was received
        TIMESTAMP:              timestamp with the format YYMMDDHHMMSS
        SIGNED-DIGEST:          The signed hash of the data

    ALLOCATE:
        This transaction type allocates a new device id and has the following format:
        ALLOCATE=TIMESTAMP

        It returns the reserved device-id in the deliver_tx method

The following query types exist:

    HISTORY:
        This query type can be used to retrieve all data of a single device, it has the following format:
        HISTORY=DEVICE-ID

        The data is returned in the following way:
        key                     stores the device-id
        value                   stores the location and timestamp, the timestamp is in the format YYMMDDHHMMSS
                                these attributes are seperated with =, it could look like this:
                                location1=timestamp1=location2=timestamp2
        
"""


from hashlib import sha256
from datetime import datetime
from ecdsa import SigningKey

BYTE_ENCODING = "UTF-8"
DATETIME_FORMAT = "%y%m%d%H%M%S"


def compute_hash(device_id: int, location: str, timestamp: datetime) -> bytes:
    hasher = sha256()
    hasher.update(bytes(device_id))
    hasher.update(bytes(location, BYTE_ENCODING))
    hasher.update(bytes(timestamp.strftime(DATETIME_FORMAT), BYTE_ENCODING))
    return hasher.digest()


def create_transaction_string(
    device_id: int, location: str, timestamp: datetime, signing_key: SigningKey
):
    return "BLOCK={}={}={}={}".format(
        device_id,
        location,
        timestamp.strftime(DATETIME_FORMAT),
        signing_key.sign(compute_hash(device_id, location, timestamp)).hex(),
    )
