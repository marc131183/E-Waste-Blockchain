from sqlitedict import SqliteDict
from hashlib import sha256

from typing import Tuple, Any


class Database:
    def __init__(self, cache_file: str = "cache.sqlite3") -> None:
        self.cache_file: str = cache_file
        with SqliteDict(self.cache_file) as dict:
            dict.clear()

    def save(self, key, value) -> Any:
        try:
            with SqliteDict(self.cache_file) as dict:
                dict[key] = value
                dict.commit()
        except Exception as ex:
            print("Error during storing data (Possibly unsupported):", ex)

    def load(self, key) -> Tuple[bool, Any]:
        try:
            with SqliteDict(self.cache_file) as dict:
                if key in dict:
                    return True, dict[key]
                else:
                    return False, None
        except Exception as ex:
            print("Error during loading data:", ex)
            return False, None

    def print(self) -> None:
        try:
            with SqliteDict(self.cache_file) as dict:
                print("Database, file = {}".format(self.cache_file))
                for key, value in dict.items():
                    print(key, value)
        except Exception as ex:
            print("Error during loading data:", ex)

    def get_hash(self) -> bytes:
        try:
            with SqliteDict(self.cache_file) as dict:
                json_str = str(dict)
                return sha256(json_str.encode()).digest()
        except Exception as ex:
            print("Error during loading data:", ex)
