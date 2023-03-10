from digital_signatures import KeyLibrary
from transactions import create_transaction_string

from datetime import datetime

if __name__ == "__main__":
    device_id = 0
    locations = ["Oslo", "Bergen"]

    keylib = KeyLibrary()

    for location in locations:
        sk, vk = KeyLibrary.create_keypair()
        keylib.add_key(location, vk)

        print(create_transaction_string(device_id, location, datetime.now(), sk))

    keylib.save("lib.txt")

    # signature = sk.sign(bytes.fromhex(hash))
    # signature = signature.hex()
    # print(vk.verify(bytes.fromhex(signature), bytes.fromhex(hash)))
