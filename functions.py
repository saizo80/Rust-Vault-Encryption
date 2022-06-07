"""General Functions"""
import os
import vault as vobj
import Rust_Vault_Encryption as rve
from password_input_window import Password_Input


def load_vaults() -> list:
    vaults = []
    config_file = os.path.expanduser(
        os.path.join('~', '.rusty-vault', 'config'))
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as file:
            for line in file:
                if line.strip():
                    temp = line.split(',')
                    temp_obj = vobj.Vault(temp[0], temp[1], temp[2])
                    vaults.append(temp_obj)

    else:
        config_folder = os.path.expanduser(os.path.join('~', '.rusty-vault'))
        if os.path.exists(config_folder):
            open(config_file, 'x', encoding='utf-8').close()
        else:
            os.mkdir(config_folder)
            open(config_file, 'x', encoding='utf-8').close()

    return vaults


def write_vaults(vaults: list):
    config_file = os.path.expanduser(
        os.path.join('~', '.rusty-vault', 'config'))

    with open(config_file, 'w', encoding='utf-8') as file:
        for i in vaults:
            file.write(f'{i.name},{i.masterFilePath},{i.hash}\n')


def readable_status(status: int) -> str:
    if status == 2:
        return 'Mixed'
    elif status == 1:
        return 'Unlocked'
    elif status == 0:
        return 'Locked'
    else:
        return 'Error'


def _get_paths(root_path: str) -> list:
    """get lists of files and folder for encryption functions"""
    file_paths = []
    dir_paths = []
    for root, dirs, files in os.walk(root_path):
        for file in files:
            if file != 'masterfile.e' and file != '.DS_Store' and not file.startswith('._'):
                file_paths.append(os.path.join(root, file))
        for dir in dirs:
            dir_paths.append(os.path.join(root, dir))
    return file_paths, dir_paths


def lock_vault(vault: vobj.Vault):
    file_paths, dir_paths = _get_paths(vault.path)
    password = Password_Input().show()

    rve.lock_vault(vault.masterFilePath, dir_paths, file_paths, password)
    vault.check_vault_status()


def unlock_vault(vault: vobj.Vault):
    file_paths, dir_paths = _get_paths(vault.path)
    password = Password_Input().show()

    rve.unlock_vault(vault.masterFilePath, dir_paths, file_paths, password)
    vault.check_vault_status()
