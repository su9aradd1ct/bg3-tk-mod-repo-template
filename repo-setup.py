import subprocess
import os
import shutil
import argparse
from pathlib import Path

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
def setup_junction(mod_name: str, sub_path: str, game_data_path: Path, repo_path: Path):
    path_in_game = game_data_path / sub_path / mod_name
    path_in_repo = repo_path / sub_path

    if not path_in_game.exists():
        print(f"{path_in_game} does not exist. Skipping.")
        return

    # Ensure the parent directory exists in the repo
    path_in_repo.parent.mkdir(parents=True, exist_ok=True)

    # Move the actual files from Game -> Repo
    print(f"Moving {path_in_game} to {path_in_repo}...")
    shutil.move(str(path_in_game), str(path_in_repo))

    """Creates a Windows Directory Junction using mklink /J."""
    print(f"Creating Junction: {path_in_game} -> {path_in_repo}")
    try:
        # mklink /J "Link" "target"
        # We use shell=True because mklink is a cmd.exe builtin
        subprocess.run(f'mklink /J "{path_in_game}" "{path_in_repo}"',
                       shell=True, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error creating junction: {e.stderr}")
        raise RuntimeError(f"Failed to link {path_in_game}")

# Remove the junction and move the files back to the game directory
def undo_junction(mod_name: str, sub_path: str, game_data_path: Path, repo_path: Path):
    path_in_game = game_data_path / sub_path / mod_name
    path_in_repo = repo_path / sub_path

    if not path_in_game.resolve() == path_in_repo:
        print(f"{path_in_game} is not a junction pointing to the {path_in_repo}. Skipping.")
        return
    if not path_in_repo.exists():
        print(f"{path_in_repo} does not exist. Skipping.")
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
    parser.add_argument("--undo", action="store_true",
                        help="Remove junctions and restore the mod files to game path")
    args = parser.parse_args()

    # Ask for confirmation
    mod_name = args.mod_name
    if args.undo:
        prompt = f"Undo repo setup by moving the files back to\n  {game_data_path}/Mods/{mod_name}?"
    else:
        prompt = f"Setup the repo by moving the files from\n  {game_data_path}/Mods/{mod_name}?"
    confirm = input(f"{prompt} (y/n): ").lower()
    if confirm != "y":
        print("Aborted")
        return

    # Check that mod project exists
    if not (game_data_path / 'Mods' / mod_name).exists():
        raise RuntimeError(f'Mod Project not found: [{mod_name}]')

    # Perform the setup or undo
    if args.undo:
        for sub_path in SUB_PATHS:
            undo_junction(mod_name, sub_path, game_data_path, repo)
        print("\nYour mod files have been restored to the game directory.")
    else:
        for sub_path in SUB_PATHS:
            setup_junction(mod_name, sub_path, game_data_path, repo)
        print("\nYour mod files are now in your repo, and the game is linked to them.")

if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        print(error)
        input("Press Enter to exit...")
