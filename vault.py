"""Object"""
from genericpath import isfile
import Rust_Vault_Encryption as rve


class Vault:
    def __init__(self, name, masterFilePath, hash):
        self.name = name
        self.masterFilePath = masterFilePath
        self.hash = hash
        self.path = masterFilePath.strip("masterfile.e")
        self.status = None
        self.check_vault_status()

    def check_vault_status(self):
        import os
        en = 0
        de = 0

        for root, dirs, files in os.walk(self.path):
            for item in files:
                if item.endswith('.encrypted') and not item.endswith('masterfile.e') and not item.endswith('.DS_Store'):
                    en += 1
                else:
                    de += 1
        if en and de:
            # mixed
            self.status = 2
        elif not en and de:
            # plaintext
            self.status = 1
        elif en and not de:
            # encrypted
            self.status = 0
        else:
            # error
            self.status = 3
