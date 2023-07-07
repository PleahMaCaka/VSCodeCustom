from os import mkdir, remove, system, path, getcwd, name as os_name, walk
import json
from zipfile import ZipFile
import subprocess as sp

try:
    from requests import get as download
except ImportError:
    system("pip install requests")
    from requests import get as download


# Configurations
PATH = getcwd()  # PATH for VSCode
BUILD = "stable"  # or insider (insider is not tested)

WIN_CODE_URL = f"https://code.visualstudio.com/sha/download?build={BUILD}&os=win32-x64-archive"
WIN_CODE_CLI_URL = f"https://code.visualstudio.com/sha/download?build={BUILD}&os=cli-win32-x64"

profile = json.load(open("profile.json", "r"))
is_windows = True if os_name == "nt" else False

# noinspection PyShadowingBuiltins
print = lambda *args, **kwargs: __builtins__.print(*args, **kwargs, flush=True)


def msg(msg): return print(f"::  {msg}")
def start(msg): return print(msg, end=" ")
def done(): return print("Done!")
def clear_console(): return system("cls" if is_windows else "clear")
def exists(p): return path.exists(p)


def cli(cmd): return (
    system(f"{PATH}\\cli\\code.exe {cmd}") if is_windows
    else system(f"{PATH}/cli/code {cmd}")
)


def download_and_extract(url, extract_path, filename):
    filename += ".zip"

    start(f"Downloading {filename}...")
    r = download(url, allow_redirects=True, stream=True)

    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    done()

    start(f"Extracting {filename}...")
    with ZipFile(filename, "r") as ref:
        ref.extractall(extract_path)
    done()

    remove(filename)


def check_vscode():
    if not exists(PATH):
        msg("Download VSCode automatically? [Y/n]")
        ans = input("===> ").lower()
        if ans == "y" or ans == "":
            if ans != "y":
                print("::  Default: Y")
            download_and_extract(WIN_CODE_URL, PATH, "VSCode")

    msg("Checking VSCode...")
    if not exists(f"{PATH}/Code.exe"):
        msg("VSCode not found. - Downloading...")
        download_and_extract(WIN_CODE_URL, PATH, "VSCode")
    else:
        msg("VSCode already exists. - Skipping.\n")


def prepare_vscode():
    if not exists(f"{PATH}/data"):
        mkdir(f"{PATH}/data")
        msg("Data folder not found. - Created.")

    if is_windows and BUILD == "stable":
        cli("version use stable --install-dir ./")
        msg("VSCode version set to stable.")
    else:
        msg("VSCode version is not stable or not Windows. - Skipping.\n")


def check_vscode_cli():
    if not exists(f"{PATH}/cli"):
        download_and_extract(WIN_CODE_CLI_URL, f"{PATH}/cli", "VSCodeCLI")
        print("::  VSCode CLI Installation completed.\n")
    else:
        msg("VSCode CLI already exists. - Skipping.\n")


def install_extensions():
    for category, ext_list in profile["extensions"].items():
        print(f"\nInstalling extensions for {category}:")
        for ext in ext_list:
            sp.run(f"cli\\code.exe ext install {ext}", stdout=sp.DEVNULL)
            ext_list = sp.run("cli\\code.exe ext list", stdout=sp.PIPE).stdout.decode(
                "utf-8").split("\n")[:-1]
            print(f"[ ✓ ] {ext}" if ext in ext_list else f"[ ✕ ] {ext}")


SETTINGS_JSON = "./data/user-data/User/settings.json"

def apply_settings():
    msg("Applying settings...")
    settings = json.load(open(SETTINGS_JSON, "r"))
    imports = []

    custom_dir = "./custom"
    for root, _, files in walk(custom_dir):
        for file in files:
            if file.endswith(".css") or file.endswith(".js"):
                if file.startswith("!"):
                    continue
                file_path = path.join(root, file)
                print(f"Importing {file}...")
                file_path = "file:///" + path.abspath(file_path.replace("\\", "/"))
                imports.append(file_path)

    settings["vscode_custom_css.imports"] = imports
    json.dump(settings, open(SETTINGS_JSON, "w"), indent=4)
    msg("Settings applied.")


if __name__ == "__main__":
    clear_console()
    if not is_windows:
        print(":: WARNING: This script is not tested on non-Windows systems. Proceed with caution.")
        print(":: Press Enter to continue.")
        input("===> ")

    check_vscode()
    check_vscode_cli()

    prepare_vscode()

    install_extensions()
    apply_settings()

    print("\nAll done!")
