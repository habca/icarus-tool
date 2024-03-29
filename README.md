# Icarus tool

The command line tool calculates total amount of resources and groups them by workstations. Tech tree has been updated after **Icarus week forty two update**.

## Getting started

Create a virtual environment and install dependencies before running the application or use the web app at <http://habca.pythonanywhere.com>.

### Linux

The `readline` package is most likely already installed as a dependency of Bash. Much like python should be pre-installed with the distribution. A creation of virtual environment is not necessary at all but here is how.

```
python -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip freeze > requirements.txt
python -m pip install -r requirements.txt

export PYTHONPATH=src

python -m unittest discover test
python -m mypy ./**/*.py
python -m black ./**/*.py
deactivate
```

### Windows

Powershell might not provide the same output as Bash shell. The reason remains unknown.

```
py -m venv .wenv
.wenv\Scripts\activate

python -m pip install --upgrade pip
python -m pip freeze > requirements.txt
python -m pip install -r requirements.txt

set PYTHONPATH=server\src

python -m unittest discover server\test
python -m mypy server\src\application.py [...]
python -m black server\src\*.py
deactivate
```

## Usage for CLI application

Program has a local command line interface and a flask app to web deployment. The configuration of the web application corresponds to the command line parameters `-i` and `-r`.

```
python application.py [options ...] [files ...]
```

The command line options supported by the program are as follows.

```
-g --gnu          Apply GNU readline functionality to python's input.
-i --implicit     Add all the necessary intermediate steps.
-j --json         Show the output of in JSON format.
-r --recursive    Show the output as a tree data structure.
-h --help         Show this user manual and exit.
```

The following lines will be displayed and program waits for a keyboard input.

```
Usage:
  amount name [+/- amount name ...]
```

## Usage for Web application

To start a backend server, run

```
python app.py
```

To start a frontend client, run

```
npm start
```

### Iterative algorithm

A comprehensive guide through the crafting process step by step.

```
> 1 stone_furnace + 1 anvil_bench + 1 machining_bench - 10 epoxy
================================================================
CHARACTER
================================================================
4 stick
----------------------------------------------------------------
1 wood
================================================================
CRAFTING BENCH
================================================================
1 stone_furnace
----------------------------------------------------------------
80 stone
12 leather
12 wood
 4 stick
================================================================
STONE FURNACE
================================================================
92 iron_ingot
----------------------------------------------------------------
184 iron_ore
================================================================
CRAFTING BENCH
================================================================
24 rope
 1 anvil_bench
----------------------------------------------------------------
288 fiber
 40 iron_ingot
 20 wood
 10 stone
================================================================
ANVIL BENCH
================================================================
120 iron_nail
----------------------------------------------------------------
12 iron_ingot
================================================================
CRAFTING BENCH
================================================================
1 machining_bench
----------------------------------------------------------------
120 iron_nail
 40 iron_ingot
 24 rope
 20 wood
 12 stone
 10 epoxy
```

### `-r` Recursive algorithm

Advanced players will find this method most intuitive.

```
> 1 stone_furnace + 1 anvil_bench + 1 machining_bench - 10 epoxy
================================================================
RECURSIVE DATA STRUCTURE
================================================================
1 stone_furnace [crafting_bench]
  4 stick [character]
    1 wood
  12 wood
  80 stone
  12 leather
----------------------------------------------------------------
1 anvil_bench [crafting_bench]
  40 iron_ingot [stone_furnace]
    80 iron_ore
  20 wood
  10 stone
----------------------------------------------------------------
1 machining_bench [crafting_bench]
  20 wood
  12 stone
  120 iron_nail [anvil_bench]
    12 iron_ingot [stone_furnace]
      24 iron_ore
  40 iron_ingot [stone_furnace]
    80 iron_ore
  24 rope [crafting_bench]
    288 fiber
```

### `-i` Implicit preprocessor

You don't have to write down the whole manufacturing process.

```
> 1 machining_bench - 10 epoxy
==============================
RECURSIVE DATA STRUCTURE
==============================
1 crafting_bench [character]
  60 fiber
  50 wood
  12 stone
  20 leather
------------------------------
1 stone_furnace [crafting_bench]
  4 stick [character]
    1 wood
  12 wood
  80 stone
  12 leather
------------------------------
1 mortar_and_pestle [crafting_bench]
  4 silica_ore
  12 stone
------------------------------
1 anvil_bench [crafting_bench]
  40 iron_ingot [stone_furnace]
    80 iron_ore
  20 wood
  10 stone
------------------------------
1 machining_bench [crafting_bench]
  20 wood
  12 stone
  120 iron_nail [anvil_bench]
    12 iron_ingot [stone_furnace]
      24 iron_ore
  40 iron_ingot [stone_furnace]
    80 iron_ore
  24 rope [crafting_bench]
    288 fiber
```

### `-j` JSON format

Data can be requested from the application in JSON format.

```
> 1 crafting_bench
[
  {
    "name": "crafting_bench",
    "amount": 1,
    "count": 1,
    "station": "character",
    "children": [
      {
        "name": "fiber",
        "amount": 60,
        "count": 1,
        "station": null,
        "children": []
      },
      {
        "name": "wood",
        "amount": 50,
        "count": 1,
        "station": null,
        "children": []
      },
      {
        "name": "stone",
        "amount": 12,
        "count": 1,
        "station": null,
        "children": []
      },
      {
        "name": "leather",
        "amount": 20,
        "count": 1,
        "station": null,
        "children": []
      }
    ]
  }
]
```

### Summary

This section lists all the raw materials to be gathered. Non-positive numbers represent the resources already found in the inventory.

```
================================================================
TOTAL RESOURCES
================================================================
  1 anvil_bench
  1 machining_bench
  1 stone_furnace
-10 epoxy
----------------------------------------------------------------
288 fiber
184 iron_ore
102 stone
 53 wood
 12 leather
```

### The most common recipes

- To fill fuel tank: `1 biofuel_composter + 1 biofuel_can + 100 fuel`
- To mine exotic deposit: `1 biofuel_generator + 1 electricity_tool + 2 electric_extractor + 1 biofuel_radar`
- To exterminate world boss: `1 hunting_rifle + 100 rifle_round`
- To resist poison: `1 carpentery_bench + 1 kitchen_bench + 2 anti-poison_pill`
- To resist cold: `1 thermos + 4 hot_coffee + 2 heat_bandage`

## Features

GNU readline provides a `TAB` completion, `^R` reverse search, `^L` clear screen, `↑↓` history search and so on.

### Automatic completion

```
> 1 biofuel_
biofuel_can                biofuel_deep-mining_drill  biofuel_generator          biofuel_radar
biofuel_composter          biofuel_extractor          biofuel_lamp               biofuel_stove
```

### Spell checker

The spell checker assists a user to find a correct spelling elegantly.

```
> 1 biofuelextractor + 1 biofuel_gen
ValueError: biofuelextractor, biofuel_gen

Did you mean?
- biofuelextractor: biofuel_extractor, biofuel_generator, biofuel_radar
- biofuel_gen: biofuel_can, biofuel_generator, biofuel_stove
```

### Recipe chooser

Program inquires a recipe if there are multiple variations for a same item.

```
> 1 fabricator
(0) mortar_and_pestle : 1 epoxy = 2 sulfur + 4 tree_sap
(1) mortar_and_pestle : 1 epoxy = 4 crushed_bone
Which recipe would you like to use? 0
```

## Development

This section explains how to set up a development environment for future references.

### Visual Studio Code

A package manager Snap provides automatic updates which is convenient, but classic confinement requires the `/snap` directory. To allow the installation of classic snaps, create a symbolic link between `/var/lib/snapd/snap` and `/snap`. [1]

```
git clone https://aur.archlinux.org/snapd.git
cd snapd
makepkg -sr
pacman -U *.pkg.tar.zst

systemctl enable --now snapd.socket
ln -s /var/lib/snapd/snap /snap
snap install code --classic
```

### Python Flask Server

- Quick Open `(Ctrl+P)`

      ext install ms-python.python

- Command Palette `(Ctrl+Shift+P)`

      Python: Select Interpreter (./.venv/bin/python)
      Python: Configure Tests (unittest > test > test_*.py)

- Settings `(Ctrl+,)`

      Testing: Automatically Open Peek View (never)
      Smart Scroll: Enabled (no)
      Formatting: provider (black)
      Editor: Format On Save (yes)
      Linting: Mypy Enabled (yes)

To change command line arguments, edit `.vscode/launch.json` file and use either `Start Debugging (F5)` or `Run Without Debugging (Ctrl+F5)`. Include a property as follows `"program": "application.py"` to run the main entry point rather than current file in the editor.

Running program in an integrated terminal (`F5`) or (`Ctrl+F5`) fails to activate and VS Code uses `Python Debug Console` instead [2]. It remains open after program completes and ceases working properly until `Python Debug Console` process is killed.

The environment variable `PYTHONPATH` must be initialized before running the python interpreter. Doing so ensures that both `Run Python File in Terminal` in Explorer and `Run Python File` in Code Editor work correctly for unit tests [3].

### JavaScript React Client

- Quick Open `(Ctrl+P)`

      ext install firefox-devtools.vscode-firefox-debug
      ext install dbaeumer.vscode-eslint
      ext install hbenl.vscode-mocha-test-adapter
      ext install esbenp.prettier-vscode

- Command Palette `(Ctrl+Shift+P)`

      ESLint: Create ESLint configuration (commonjs, defaults)

### Visual Studio Community

To change command line arguments, edit `Project > Properties > Debug > Script Arguments` field and use either `Start Debugging (F5)` or `Start Without Debugging (Ctrl+F5)`.

For me, there was a major problem detecting breakpoints when debugging test case with an infinite loop. Test explorer froze up effectively preventing any further testing.

## Deployment

### Client

The server hosts the client-side application as a static website to avoid CORS issues. To deploy on production environment, run

```
npm install
npm run build
```

### Server

Startup command installs requirements into a virtual environment and launches a flask application from the source folder using a production dedicated server `Gunicorn`.

```
python -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

export PYTHONPATH=src
gunicorn --bind=0.0.0.0 --timeout 600 app:app
```

### PythonAnywhere

Hosting a static website requires `node` and `npm`. Here is how to install `v18.12.1` for reference, but one should choose the latest LTS.

```
git clone --depth 1 https://github.com/creationix/nvm.git
source ~/nvm/nvm.sh

nvm ls-remote
nvm install v18.12.1
nvm use v18.12.1
nvm alias default v18.12.1

rm -r node_modules
rm package-lock.json

npm install react-scripts
npm install
npm run build
```

### Azure

Due to the project structure of the source code, the python interpreter must be set to use the PYTHONPATH environment variable. App Service deployment engine automatically activates a virtual environment and runs `pip install -r requirements.txt` [4]. Production use of Azure requires a paid subscription.

## References

- [1] <https://wiki.archlinux.org/title/Snap#Classic_snaps>
- [2] <https://github.com/microsoft/vscode/issues/158218>
- [3] <https://code.visualstudio.com/docs/python/environments#_use-of-the-pythonpath-variable>
- [4] <https://learn.microsoft.com/en-us/azure/app-service/configure-language-python>
