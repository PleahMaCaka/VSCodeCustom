import os
import random
from os import path
from zipfile import ZipFile

try:
    import requests
except ImportError:
    os.system("pip install requests")
    import requests

is_windows: bool

if os.name == "nt":
    is_windows = True

# noinspection PyShadowingBuiltins
print = lambda *args, **kwargs: __builtins__.print(*args, **kwargs, flush=True)


def start(msg): return print(msg, end=" ")
def done(): return print("Done!")


# VSC CONFIG
CODE_PATH = "./"
BUILD = "insider"  # or {BUILD}

WIN_CODE_URL = f"https://code.visualstudio.com/sha/download?build={BUILD}&os=win32-x64-archive"


def clear_console():
    if is_windows:
        os.system("cls")
    else:
        os.system("clear")


def download_and_extract(download_url, extract_path, filename):
    filename += ".zip"

    start(f"Downloading {filename}...")
    r = requests.get(download_url, allow_redirects=True, stream=True)

    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    done()

    start(f"Extracting {filename}...")
    with ZipFile(filename, "r") as ref:
        ref.extractall(extract_path)
    done()

    os.remove(filename)


def check_vscode():
    if path.exists(CODE_PATH):
        print("::  VSCode already exists. Skipped.")
        print("::  Checking if Code.exe exists...")
        if not path.exists(f"{CODE_PATH}/Code.exe"):
            print("::  Code.exe does not exist. Proceeding with installation.")
            download_and_extract(
                WIN_CODE_URL,
                CODE_PATH, "VSCode"
            )
    else:
        print("::  VSCode does not exist. Download automatically? [Y/n]")
        ans = input("===> ").lower()
        if ans == "y" or ans == "":
            if ans != "y":
                print("::  Default: Y")
            download_and_extract(
                WIN_CODE_URL,
                CODE_PATH, "VSCode"
            )
        else:
            print("::  Skipping VSCode download.")


def prepare_vscode():
    if not path.exists(f"{CODE_PATH}/data"):
        os.mkdir(f"./{CODE_PATH}/data")
        print("Data folder not found. Created.")


def main():
    if not is_windows:
        print(":: WARNING: This script is not tested on non-Windows systems. Proceed with caution.")
        print(":: Press Enter to continue.")
        input("===> ")

    clear_console()
    check_vscode()
    prepare_vscode()

    download_and_extract(
        f"https://code.visualstudio.com/sha/download?build={BUILD}&os=cli-win32-x64",
        f"{CODE_PATH}/cli", "VSCodeCLI"  # extract to code root
    )
    print("::  VSCode CLI Installation completed.")


if __name__ == "__main__":
    main()
    print("All done!")
