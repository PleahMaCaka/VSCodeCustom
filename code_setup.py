import os
import random
from os import path
from zipfile import ZipFile

import requests

# noinspection PyShadowingBuiltins
print = lambda *args, **kwargs: __builtins__.print(*args, **kwargs, flush=True)

CODE_PATH = "./"


def clear_console():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def download_and_extract(download_url, extract_path, filename):
    filename += ".zip"
    print(f"Download {filename}...", end="")
    r = requests.get(download_url, allow_redirects=True, stream=True)

    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    print("Done!")

    print("Extracting...", end="")
    with ZipFile(filename, "r") as ref:
        ref.extractall(extract_path)
    print("Done!")

    os.remove(filename)


def check_vscode():
    if not path.exists(CODE_PATH):
        print("::  VSCode does not exist. Download automatically? [Y/n]")
        ans = input("===> ").lower()
        if ans == "y" or ans == "":
            if ans != "y":
                print("::  Default: Y")
            download_and_extract(
                "https://code.visualstudio.com/sha/download?build=stable&os=win32-x64-archive",
                CODE_PATH, "VSCode"
            )
        else:
            print("::  Skipping VSCode download.")
    else:
        print("::  VSCode already exists. Skipped.")
        print("::  Checking if Code.exe exists...")
        if path.exists(f"{CODE_PATH}/Code.exe"):
            print("::  Code.exe exists. Proceed with installation? [Y/n]")
            ans = input("===> ").lower()
            if ans == "y":
                random_number = str(random.randint(100, 999))
                print(f"::  Enter the random 3-digit number to proceed: [{random_number}]")
                user_input = input("===> ")
                if user_input == random_number:
                    download_and_extract(
                        "https://code.visualstudio.com/sha/download?build=stable&os=win32-x64-archive",
                        CODE_PATH, "VSCode"
                    )
                    print("::  VSCode Installation completed.")
                else:
                    print("::  Random number verification failed. Installation aborted.")
            else:
                print("::  Skipping installation.")
        else:
            print("::  Code.exe does not exist. Proceeding with installation.")
            download_and_extract(
                "https://code.visualstudio.com/sha/download?build=stable&os=win32-x64-archive",
                CODE_PATH, "VSCode"
            )


def create_data_folder():
    if not path.exists(f"{CODE_PATH}/data"):
        os.mkdir("./VSCode/data")
        print("Data folder not found. Created.")


def main():
    clear_console()
    check_vscode()
    create_data_folder()

    download_and_extract(
        "https://code.visualstudio.com/sha/download?build=stable&os=cli-win32-x64",
        CODE_PATH, "VSCodeCLI"  # extract to code root
    )
    print("::  VSCode CLI Installation completed.")


if __name__ == "__main__":
    main()
    print("All done!")
