import subprocess
import sys
import shutil
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

def create_junction(link_path: Path, target_path: Path):
    """Creates a Windows Directory Junction using mklink /J."""
    print(f"Creating Junction: {link_path} -> {target_path}")
    try:
        # mklink /J "Link" "target"
        # We use shell=True because mklink is a cmd.exe builtin
        subprocess.run(f'mklink /J "{link_path}" "{target_path}"',
                       shell=True, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error creating junction: {e.stderr}")
        raise RuntimeError(f"Failed to link {link_path}")

def main():
    # Check that Game path is valid
    game_data_path = Path(GAME_DATA_ROOT)
    if not game_data_path.exists():
        raise RuntimeError(f'Game Data path invalid: [{GAME_DATA_ROOT}]')

    repo = Path(".").resolve()
    mod_name = MOD_NAME_FULL or repo.name

    # Ask for confirmation
    print(f"Mod name: {mod_name}")
    confirm = input(f"{mod_name} (y/n): ").lower()
    if confirm != "y":
        print("Aborted")
        return

    # Check that mod project exists
    if not (game_data_path / 'Mods' / mod_name).exists():
        raise RuntimeError(f'Mod Project not found: [{mod_name}]')

    # Migration and linking
    for sub_path in SUB_PATHS:
        # The specific folder for THIS mod inside the game directory
        source_in_game = game_data_path / sub_path / mod_name
        # The destination folder in your Git Repo
        dest_in_repo = repo / sub_path

        if source_in_game.exists():
            print(f"Moving {sub_path} data to repo...")

            # Ensure the parent directory exists in the repo
            dest_in_repo.parent.mkdir(parents=True, exist_ok=True)

            # Move the actual files from Game -> Repo
            shutil.move(str(source_in_game), str(dest_in_repo))

            # Create the Junction in the Game folder pointing to the Repo
            create_junction(source_in_game, dest_in_repo)
        else:
            print(f"Skipping {sub_path}: Folder not found in game data.")

    print("\nSuccess! Your mod files are now in your repo, and the game is linked to them.")

if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        print(error)
        input("Press Enter to exit...")
