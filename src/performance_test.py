import grequests

from digital_signatures import KeyLibrary
from transactions import DATETIME_FORMAT, allocate_device_id, compute_hash

import sys
import random
import time
from datetime import datetime


if __name__ == "__main__":
    num_tx = int(sys.argv[1])

    with open("my_location.txt", "r") as file:
        my_location = file.readlines()[0]
    sk = KeyLibrary.load_signing_key("priv_key.pem")

    allocate_device_id(my_location)
    max_device_id = 0

    urls = []
    for i in range(num_tx):
        if random.randint(0, 2):
            now = datetime.now()
            device_id = random.randint(0, max_device_id)
            destruct = False
            transaction_string = "BLOCK={}={}={}={}={}".format(
                device_id,
                my_location,
                now.strftime(DATETIME_FORMAT),
                destruct,
                sk.sign(compute_hash(device_id, my_location, now, destruct)).hex(),
            )
            urls.append(
                'http://localhost:26657/broadcast_tx_commit?tx="{}"'.format(
                    transaction_string
                )
            )
        else:
            urls.append(
                'http://localhost:26657/broadcast_tx_commit?tx="ALLOCATE={}={}"'.format(
                    my_location, datetime.now().strftime(DATETIME_FORMAT)
                )
            )
            max_device_id += 1

    start_time = time.time()

    rs = (grequests.get(u) for u in urls)
    grequests.map(rs)

    total_time = time.time() - start_time
    print(
        "Time to execute {} requests: {} -> tx/s = {}".format(
            num_tx, total_time, num_tx / total_time
        )
    )
