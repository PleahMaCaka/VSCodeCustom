import os
import json
from os import path
from zipfile import ZipFile
import subprocess

try:
    import requests
except ImportError:
    os.system("pip install requests")
    import requests


# VSC CONFIG
CODE_PATH = os.getcwd()
BUILD = "stable"  # or insider (insider is not tested)

WIN_CODE_URL = f"https://code.visualstudio.com/sha/download?build={BUILD}&os=win32-x64-archive"
WIN_CODE_CLI_URL = f"https://code.visualstudio.com/sha/download?build={BUILD}&os=cli-win32-x64"

profile = json.load(open("profile.json", "r"))
is_windows = True if os.name == "nt" else False

# noinspection PyShadowingBuiltins
print = lambda *args, **kwargs: __builtins__.print(*args, **kwargs, flush=True)


def start(msg): return print(msg, end=" ")
def done(): return print("Done!")
def msg(msg): return print(f"::  {msg}")


def cli(cmd):
    if is_windows:
        os.system(f"{CODE_PATH}\\cli\\code.exe {cmd}")
    else:
        os.system(f"{CODE_PATH}/cli/code {cmd}")


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
    if not path.exists(CODE_PATH):
        msg("Download VSCode automatically? [Y/n]")
        ans = input("===> ").lower()
        if ans == "y" or ans == "":
            if ans != "y":
                print("::  Default: Y")
            download_and_extract(WIN_CODE_URL, CODE_PATH, "VSCode")

    msg("Checking VSCode...")
    if not path.exists(f"{CODE_PATH}/Code.exe"):
        msg("VSCode not found. - Downloading...")
        download_and_extract(WIN_CODE_URL, CODE_PATH, "VSCode")
    else:
        msg("VSCode already exists. - Skipping.")


def prepare_vscode():
    if not path.exists(f"{CODE_PATH}/data"):
        os.mkdir(f"{CODE_PATH}/data")
        msg("Data folder not found. - Created.")

    if is_windows and BUILD == "stable":
        cli("version use stable --install-dir ./")
        msg("VSCode version set to stable.")
    else:
        msg("VSCode version is not stable or not Windows. - Skipping.")


def install_vscode_cli():
    download_and_extract(WIN_CODE_CLI_URL, f"{CODE_PATH}/cli", "VSCodeCLI")
    print("::  VSCode CLI Installation completed.")


def install_extensions():
    for ext in profile["extensions"]:
        start(f"Installing {ext}...")
        subprocess.run(f"cli\\code.exe ext install {ext}", shell=True, stdout=subprocess.DEVNULL)
        done()
    msg("===> Installed extensions:")
    cli("ext list")
    # save result of 'ext list' and split \n and compare with profile["extensions"]
    res = subprocess.run("cli\\code.exe ext list", shell=True, stdout=subprocess.PIPE)

    msg("===> Not installed extensions:")
    res = res.stdout.decode("utf-8").split("\n")
    for ext in res:
        if ext not in profile["extensions"]:
            msg(ext)

def install_vscode():
    check_vscode()
    prepare_vscode()
    install_vscode_cli()

    install_extensions()


def main():
    if not is_windows:
        print(":: WARNING: This script is not tested on non-Windows systems. Proceed with caution.")
        print(":: Press Enter to continue.")
        input("===> ")

    clear_console()
    install_vscode()

    print("All done!")


if __name__ == "__main__":
    main()
