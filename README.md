# bg3-tk-mod-repo-template

Git repo template for Baldur's Gate 3 Toolkit projects.

`repo-setup.py` makes it easy to keep your mod files safe in one folder managed by Git, while still allowing the **Baldur's Gate 3 Toolkit** to continue to work on them.


## What it does
1. **Moves your work to a central location:** It takes your mod folders (i.e. Mods, Public, Editor/Mods, Projects) scattered across different locations in the game folder and moves them under one folder.
2. **Creates "shortcut folders" called [junctions](https://learn.microsoft.com/en-us/windows/win32/fileio/hard-links-and-junctions#junctions):** It places a special type of shortcut back into the Game Data directory where the mod folders used to be, so that the game and the toolkit *think* the files are still in the original spot.

For example, if your set up your Git folder at
```
C:\Users\me\Documents\BG3\Mods\YourModNameHere_857aee99-5f79-fd6e-bf15-8c41e6863b1b
```
then
```
C:\Program Files (x86)\Steam\steamapps\common\Baldurs Gate 3\Data\Mods\YourModNameHere_857aee99-5f79-fd6e-bf15-8c41e6863b1b
```
would point to
```
C:\Users\me\Documents\BG3\Mods\YourModNameHere_857aee99-5f79-fd6e-bf15-8c41e6863b1b\Mods
```

### Why

You get all the benefits of having your files under version control, while continuing to work on your mod project with the toolkit.
- **Safety:** You can be assured that all your files are backed up
- **Convenience:** You can easily undo a change that broke your mod with Git and go back to an earlier version, and see all your work history.
- **Organization:** It's easy to keep track of your changes in once place

## Required Dependencies
- Python runtime
  - https://www.python.org/downloads/
- Git
  - https://git-scm.com/downloads
  - There are other clients as well, such as https://desktop.github.com/download/


## How to Use

For more info regarding the usages of the `repo-setup.py` script in general, run
```
python repo-setup.py --help
```

### Set up Repo
1. [Create a new mod project](https://baldursgate3.game/mods#/r/getting-started-creating-a-new-mod) in the Baldur's Gate 3 Toolkit
2. [Create a new repository from the template](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template)
3. Clone the new repo to a non-protected directory (not in something like Program Files) like `Documents`. Match the name of the repo directory to match the name of the mod, e.g. `YourModNameHere_857aee99-5f79-fd6e-bf15-8c41e6863b1b`.

    **OPTIONAL:** If needed, update `GAME_DATA_ROOT` and `MOD_NAME_FULL` properties at the top of `repo-setup.py` and save.
    ```diff
    """
    GAME_DATA_ROOT: str = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Baldurs Gate 3\\Data"
    -MOD_NAME_FULL: str = "" # Defaults to the current repo directory name
    +MOD_NAME_FULL: str = "YourModNameHere_857aee99-5f79-fd6e-bf15-8c41e6863b1b" # Defaults to the current repo directory name
    ```
5. From the command prompt, run
    ```
    python repo-setup.py [MOD_NAME_FULL]
    ```
    Or, double-click on the script
6. Going forward you should be able to commit/push/pull/etc. like any other git repo

### Undo set up repo
1. Run
    ```
    python repo-setup.py [MOD_NAME_FULL] --undo
    ```
   This removes all the junction shortcuts and moves all the mod directories back to its original location in the game data directory.

### Set up project from repo
1. Run
    ```
    python repo-setup.py [MOD_NAME_FULL] --from-repo
    ```
    This creates all the junctions in places pointing to the current repo.

> [!NOTE]
> If the project isn't showing up on the toolkit, make sure the Project data folder (`/Data/Projects`) and `meta.lsx` are properly in place.
