from typing import Dict, Tuple
from ecdsa import SigningKey, VerifyingKey, NIST256p

CURVE = NIST256p


class KeyLibrary:
    def __init__(self) -> None:
        self.map: Dict[str, VerifyingKey] = {}

    def load(self, path: str) -> None:
        with open(path, "r") as f:
            for line in f.readlines():
                loc, key, destruct, lat, lon = line.split(":")
                key = bytes.fromhex(key)
                self.map[loc] = (
                    VerifyingKey.from_string(key, curve=CURVE),
                    bool(destruct[:-1]),
                    lat,
                    lon,
                )

        f.close()

    def save(self, path: str) -> None:
        with open(path, "w+") as f:
            for key, value in self.map.items():
                f.write(
                    key
                    + ":"
                    + str(value[0].to_string().hex())
                    + ":"
                    + value[1]
                    + ":"
                    + value[2]
                    + ":"
                    + value[3]
                    + "\n"
                )
        f.close()

    @staticmethod
    def create_keypair() -> Tuple[SigningKey, VerifyingKey]:
        sk: SigningKey = SigningKey.generate(curve=CURVE)
        vk: VerifyingKey = sk.verifying_key
        return (sk, vk)

    @staticmethod
    def save_signing_key(path: str, key: SigningKey) -> None:
        b: bytes = key.to_pem()
        with open(path, "wb") as file:
            file.write(b)

    @staticmethod
    def load_signing_key(path: str) -> SigningKey:
        with open(path, "rb") as file:
            b: bytes = file.read()
        return SigningKey.from_pem(b)

    def add_key(
        self, location: str, key: VerifyingKey, destruct: bool, lat: float, lon: float
    ) -> None:
        self.map[location] = (key, destruct, lat, lon)

    def verify(self, location: str, message: bytes, signature: bytes) -> bool:
        if location in self.map:
            try:
                return self.map[location][0].verify(signature, message)
            except:
                return False
        return False

    def has_destruct_certificate(self, location: str) -> bool:
        if location in self.map:
            return self.map[location][1]
        return False

    def get_coordinates(self, location: str) -> Tuple[bool, float, float]:
        if location in self.map:
            return (True, self.map[location][2], self.map[location][3])
        return (False, 0, 0)
