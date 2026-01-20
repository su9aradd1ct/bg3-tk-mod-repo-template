import subprocess
import os
import shutil
import argparse
from pathlib import Path

"""
    https://github.com/su9aradd1ct/bg3-tk-mod-repo-template

    Copyright (c) 2025 xiphiasrex
    Portions Copyright (c) 2026 su9aradd1ct

    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

"""
    Update these properties if needed.
    Run it from repo directory root with `python repo-setup.py`.

    GAME_DATA_ROOT: Path to your BG3 Data folder
    MOD_NAME_FULL: Full project name with UUID, e.g. YourModNameHere_857aee99-5f79-fd6e-bf15-8c41e6863b1b
"""
GAME_DATA_ROOT: str = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Baldurs Gate 3\\Data"
MOD_NAME_FULL: str = "" # Defaults to the current repo directory name

"""
    *** Unless you know what you are doing don't modify below here!! ***
"""
# List of sub-paths that BG3 modding typically uses
SUB_PATHS = [
    Path("Mods"), # game data folder
    Path("Public"), # resource data folder
    Path("Editor") / "Mods", # editor data folder
    Path("Projects"), # project data folder
]

# Move the mod files from the game directory to the repo, and create a junction
def move_dirs_and_setup_junction(mod_name: str, sub_path: str, game_data_path: Path, repo_path: Path, interactive: bool):
    path_in_game = game_data_path / sub_path / mod_name
    path_in_repo = repo_path / sub_path

    if not path_in_game.exists():
        print(f"{path_in_game} does not exist. Skipping.")
        return

    if interactive:
        confirm = input(f"Move `{path_in_game}` to `{path_in_repo}`? (y/n): ").lower()
        if confirm != "y":
            return

    # Ensure the parent directory exists in the repo
    path_in_repo.parent.mkdir(parents=True, exist_ok=True)

    # Move the actual files from Game -> Repo
    print(f"Moving {path_in_game} to {path_in_repo}...")
    shutil.move(str(path_in_game), str(path_in_repo))

    create_junction(path_in_game, path_in_repo)

# Create a junction in game dir pointing to the repo
def setup_junction(mod_name: str, sub_path: str, game_data_path: Path, repo_path: Path, interactive: bool):
    path_in_game = game_data_path / sub_path / mod_name
    path_in_repo = repo_path / sub_path

    # Ensure that the directory doesn't already exist
    if path_in_game.exists():
        print(f"{path_in_game} already exists. Skipping.")
        return

    if interactive:
        confirm = input(f"Create junction {path_in_game} -> {path_in_repo}? (y/n): ").lower()
        if confirm != "y":
            return

    # Ensure that the directory exists in the repo
    path_in_repo.mkdir(parents=True, exist_ok=True)

    create_junction(path_in_game, path_in_repo)

def create_junction(link: str, target: str):
    """Creates a Windows Directory Junction using mklink /J."""
    print(f"Creating Junction: `{link}` -> `{target}`")
    try:
        # mklink /J "Link" "target"
        # We use shell=True because mklink is a cmd.exe builtin
        subprocess.run(f'mklink /J "{link}" "{target}"',
                       shell=True, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error creating junction: {e.stderr}")
        raise RuntimeError(f"Failed to link {link}")

# Remove the junction and move the files back to the game directory
def undo_junction(mod_name: str, sub_path: str, game_data_path: Path, repo_path: Path, interactive: bool):
    path_in_game = game_data_path / sub_path / mod_name
    path_in_repo = repo_path / sub_path

    if not path_in_game.resolve() == path_in_repo:
        print(f"{path_in_game} is not a junction pointing to the {path_in_repo}. Skipping.")
        return
    if not path_in_repo.exists():
        print(f"{path_in_repo} does not exist. Skipping.")
        return

    if interactive:
        confirm = input(f"Restore `{path_in_repo}` to `{path_in_game}`? (y/n): ").lower()
        if confirm != "y":
            return

    os.rmdir(path_in_game)
    shutil.move(str(path_in_repo), str(path_in_game))
    print(f"Removed the junction and moved the data back to {path_in_game}")

def main():
    # Check that Game path is valid
    game_data_path = Path(GAME_DATA_ROOT)
    if not game_data_path.exists():
        raise RuntimeError(f'Game Data path invalid: [{GAME_DATA_ROOT}]')

    # Parse arguments
    repo = Path(".").resolve()
    parser = argparse.ArgumentParser(description="Set up repo by moving the mod files from the game directory and replacing with junctions.")
    parser.add_argument("mod_name", nargs="?",  default=(MOD_NAME_FULL or repo.name),
                        help=f"Name of the mod folder in GAME_DATA_ROOT (default: MOD_NAME_FULL or current directory name)")
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="Promopt for confirmation for each action")

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--undo", action="store_true",
                        help="Remove junctions and restore the mod files to game path")
    mode.add_argument("--from-repo", action="store_true",
                        help="Set up the project by creating junctions in the game directory. Will fail if the directory already exists in the game directory.")

    args = parser.parse_args()

    # Ask for confirmation
    mod_name = args.mod_name
    if args.undo:
        prompt = f"Undo repo setup by moving the files back to\n  {game_data_path}/Mods/{mod_name}?"
    elif args.from_repo:
        prompt = f"Setup the project from repo by creating junctions in\n  {game_data_path}/Mods/{mod_name}?"
    else:
        prompt = f"Setup the repo by moving the files from\n  {game_data_path}/Mods/{mod_name}?"
    confirm = input(f"{prompt} (y/n): ").lower()
    if confirm != "y":
        print("Aborted")
        return

    # Check that mod project exists
    if not args.from_repo and not (game_data_path / 'Mods' / mod_name).exists():
        raise RuntimeError(f'Mod Project not found: [{mod_name}]')

    # Perform the setup or undo
    if args.undo:
        for sub_path in SUB_PATHS:
            undo_junction(mod_name, sub_path, game_data_path, repo, interactive = args.interactive)
        print("\nYour mod files have been restored to the game directory.")
    elif args.from_repo:
        for sub_path in SUB_PATHS:
            setup_junction(mod_name, sub_path, game_data_path, repo, interactive = args.interactive)
        print("\nYour mod files are now in your repo, and the game is linked to them.")
    else:
        for sub_path in SUB_PATHS:
            move_dirs_and_setup_junction(mod_name, sub_path, game_data_path, repo, interactive = args.interactive)
        print("\nYour mod files are now in your repo, and the game is linked to them.")

if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        print(error)
        input("Press Enter to exit...")
