from typing import Dict, Tuple
from ecdsa import SigningKey, VerifyingKey, NIST256p

CURVE = NIST256p


class KeyLibrary:
    def __init__(self) -> None:
        self.map: Dict[str, VerifyingKey] = {}

    def load(self, path: str) -> None:
        with open(path, "r") as f:
            for line in f.readlines():
                key, value = line.split(":")
                value = bytes.fromhex(value[:-1])
                self.map[key] = VerifyingKey.from_string(value, curve=CURVE)

        f.close()

    def save(self, path: str) -> None:
        with open(path, "w+") as f:
            for key, value in self.map.items():
                f.write(key + ":" + str(value.to_string().hex()) + "\n")
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

    def add_key(self, location: str, key: VerifyingKey) -> None:
        self.map[location] = key

    def verify(self, location: str, message: bytes, signature: bytes) -> bool:
        if location in self.map:
            try:
                return self.map[location].verify(signature, message)
            except:
                return False
        return False
