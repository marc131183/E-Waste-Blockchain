from transactions import compute_hash, DATETIME_FORMAT, BYTE_ENCODING
from digital_signatures import KeyLibrary
from database import Database

from types_pb2 import (
    RequestInfo,
    ResponseInfo,
    RequestInitChain,
    ResponseInitChain,
    RequestCheckTx,
    ResponseCheckTx,
    RequestDeliverTx,
    ResponseDeliverTx,
    RequestQuery,
    ResponseQuery,
    RequestCommit,
    ResponseCommit,
)
from abci.server import ABCIServer
from abci.application import BaseApplication, OkCode, ErrorCode
from datetime import datetime
from typing import Dict, List, Tuple


class WasteTracker(BaseApplication):
    def init_chain(self, req: RequestInitChain) -> ResponseInitChain:
        self.keys: KeyLibrary = KeyLibrary()
        self.keys.load("lib.txt")
        self.num_items: int = 0
        self.uncommited_transactions: Dict[int, List[Tuple[str, datetime, str]]] = {}
        self.db = Database()

        return ResponseInitChain()

    def check_tx(self, tx: bytes) -> ResponseCheckTx:
        split = tx.decode(BYTE_ENCODING).split("=")

        if split[0] == "BLOCK":
            device_id: int = int(split[1])
            location: str = split[2]
            timestamp: datetime = datetime.strptime(split[3], DATETIME_FORMAT)
            destruct: bool = split[4] == "True"
            signature: bytes = bytes.fromhex(split[5])

            hash: bytes = compute_hash(device_id, location, timestamp, destruct)

            # verify that the transaction was created by the location's node and that the content is correct
            if not self.keys.verify(location, hash, signature):
                return ResponseCheckTx(code=ErrorCode, log="signature incorrect")

            # verify that the location has a destruction certificate, if the item ordered to be destroyed there
            if destruct:
                if not self.keys.has_destruct_certificate(location):
                    return ResponseCheckTx(
                        code=ErrorCode,
                        log="item is ordered to be destroyed, but location does not have a valid destruction certificate",
                    )

            # verify that the device id is assigned
            if device_id >= self.num_items:
                return ResponseCheckTx(code=ErrorCode, log="device-id not assigned")

            # verify that the last location of that device is not the same as the one broadcasted and that the item has not been destroyed yet
            exists, device_info = self.db.load(device_id)
            if exists and len(device_info):
                if device_info[-1][0] == location:
                    return ResponseCheckTx(
                        code=ErrorCode,
                        log="last location of device equals the submitted one",
                    )
                if device_info[-1][2]:
                    return ResponseCheckTx(
                        code=ErrorCode,
                        log="item has already been destroyed, cannot add entry",
                    )

            return ResponseCheckTx(code=OkCode)
        elif split[0] == "ALLOCATE":
            return ResponseCheckTx(code=OkCode)
        else:
            return ResponseCheckTx(code=ErrorCode, log="unsupported transaction type")

    def deliver_tx(self, tx: bytes) -> ResponseDeliverTx:
        split = tx.decode(BYTE_ENCODING).split("=")

        if split[0] == "BLOCK":
            device_id: int = int(split[1])
            location: str = split[2]
            timestamp: datetime = datetime.strptime(split[3], DATETIME_FORMAT)
            destruct: bool = split[4] == "True"
            signature: str = split[5]

            if device_id in self.uncommited_transactions:
                self.uncommited_transactions[device_id].append(
                    (location, timestamp, destruct, signature)
                )
            else:
                self.uncommited_transactions[device_id] = [
                    (
                        location,
                        timestamp,
                        destruct,
                        signature,
                    )
                ]

            return ResponseDeliverTx(code=OkCode)
        elif split[0] == "ALLOCATE":
            self.num_items += 1
            return ResponseDeliverTx(
                code=OkCode, data=bytes(str(self.num_items - 1), BYTE_ENCODING)
            )
        else:
            return ResponseDeliverTx(code=ErrorCode, log="unsupported transaction type")

    def query(self, req: RequestQuery) -> ResponseQuery:
        split = req.data.decode(BYTE_ENCODING).split("=")

        if split[0] == "HISTORY":
            device_id: int = int(split[1])

            if device_id >= self.num_items:
                return ResponseQuery(code=ErrorCode, log="device-id not assigned")

            exists, history = self.db.load(device_id)

            if not exists:
                return ResponseQuery(
                    code=OkCode,
                    key=bytes(str(device_id), BYTE_ENCODING),
                    info="device-id assigned, but no data available",
                )

            value = ""
            for i, (location, timestamp, destruct, signature) in enumerate(history):
                value = (
                    value
                    + "=" * (i != 0)
                    + "{}={}".format(
                        location + (" - destroyed" if destruct else ""),
                        timestamp.strftime(DATETIME_FORMAT),
                    )
                )
                # verify signature to check that data hasn't been changed
                hash: bytes = compute_hash(device_id, location, timestamp, destruct)

                if not self.keys.verify(location, hash, bytes.fromhex(signature)):
                    return ResponseQuery(
                        code=ErrorCode,
                        log="signature of ({}, {}) incorrect".format(
                            location, timestamp
                        ),
                    )

            return ResponseQuery(
                code=OkCode,
                key=bytes(str(device_id), BYTE_ENCODING),
                value=bytes(value, BYTE_ENCODING),
            )
        elif split[0] == "NUMBER":
            return ResponseQuery(
                code=OkCode, value=bytes(str(self.num_items - 1), BYTE_ENCODING)
            )
        else:
            return ResponseQuery(code=ErrorCode, log="unsupported query type")

    def commit(self) -> ResponseCommit:
        self.db.save("num_devices", self.num_items)
        for key, value in self.uncommited_transactions.items():
            exists, old_value = self.db.load(key)
            if exists:
                self.db.save(key, old_value + value)
            else:
                self.db.save(key, value)
        self.uncommited_transactions = {}
        return ResponseCommit(data=self.db.get_hash())


if __name__ == "__main__":
    app = ABCIServer(app=WasteTracker())
    app.run()
