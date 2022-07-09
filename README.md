## Getting started

Create a virtual environment and install dependencies before running the application.
An unit testing framework `unittest` and a static code analysis tool `mypy` proved to be very useful in the developing process.

### Windows

```
py -m venv .venv
.venv\Scripts\activate
python -m pip install pyreadline
python -m pip install mypy

python -m unittest
python -m mypy application.py
python application.py -g <inputfile>
deactivate
```

### Linux

The readline package is most likely already installed as a dependency of Bash. Much like python should be pre-installed with the distribution. A creation of virtual environment is not necessary at all but here is how.

```
python -m venv .venv
source .venv/bin/activate
python -m pip install readline
python -m pip install mypy

python -m unittest
python -m mypy application.py
python application.py -g <inputfile>
deactivate
```

## Usage

```
python application.py -g data/tech_tree.txt
```

The command line options supported by the program are as follows.

```
-g --gnu    Apply GNU readline functionality to python's input.
```

The manual will be displayed and program waits for a keyboard input.

```
Welcome to use Icarus tool
--------------------------
amount name = amount name [+ amount name]
amount name [+ amount name]

> 
```

## Features

GNU readline provides a `TAB` completion, `^R` reverse search, `↑↓` history search and so on.

```
> 1 biofuel_
biofuel_can       biofuel_composter biofuel_extractor biofuel_generator
> 1 biofuel_extractor + 1 biofuel_
biofuel_can       biofuel_composter biofuel_extractor biofuel_generator
> 1 biofuel_extractor + 1 biofuel_generator
-------------------------------------------
21 steel_ingot
20 steel_screw
17 refined_gold
15 iron_ingot
12 electronics
10 copper_nail
 8 copper_ingot
 2 glass
-------------------------------------------
156 iron_ore
 45 copper_ingot
 24 epoxy
 24 organic_resin
  2 silica_ore
-------------------------------------------
96 tree_sap
90 copper_ore
63 wood
48 sulfur
34 gold_ore
24 oxite
21 steel_bloom
-------------------------------------------
384 stick
 21 coal_ore
-------------------------------------------

TOTAL RESOURCES
-------------------------------------------
156 iron_ore
 90 copper_ore
 63 wood
 48 sulfur
 34 gold_ore
 24 oxite
 21 coal_ore
  2 silica_ore
```

The spell checker assists a user to find a correct spelling elegantly.

```
> 1 biofuelextractor + 1 biofuel_gen
ValueError: biofuelextractor

Did you mean?
- biofuelextractor: biofuel_extractor, biofuel_generator, electric_extractor
- biofuel_gen: biofuel_can, biofuel_generator
```

## Developers

### Visual Studio Code

To change command line arguments, edit `.vscode/launch.json` file and use either `Start Debugging (F5)` or `Run Without Debugging (Ctrl+F5)`. Include a property as follows `"program": "application.py"` to run the main entry point rather than current file in editor.
