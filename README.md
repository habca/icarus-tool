# Icarus tool

The command line tool calculates total amount of resources and groups them by workstations.

## Getting started

Create a virtual environment and install dependencies before running the application.
A unit testing framework `unittest` and a static code analysis tool `mypy` proved to be very useful in the developing process. The source code formatter `black` makes visual styling decisions much easier.

### Windows

```
py -m venv .venv
.venv\Scripts\activate
python -m pip install pyreadline
python -m pip install mypy
python -m pip install black

python -m unittest
python -m mypy application.py calculator.py test_application.py test_calculator.py
python -m black *.py
python application.py -g <inputfile>
deactivate
```

### Linux

The `readline` package is most likely already installed as a dependency of Bash. Much like python should be pre-installed with the distribution. A creation of virtual environment is not necessary at all but here is how.

```
python -m venv .venv
source .venv/bin/activate
python -m pip install readline
python -m pip install mypy
python -m pip install black

python -m unittest
python -m mypy *.py
python -m black *.py
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
Welcome to Icarus tool!
-----------------------
amount name [+ amount name]

> 
```

## The most common recipes

- To fill fuel tank: `1 biofuel_composter + 1 biofuel_can + 100 fuel`
- To mine exotic deposit: `1 biofuel_generator + 1 electricity_tool + 1 electric_extractor`
- To exterminate world boss: `1 hunting_rifle + 100 rifle_round`
- To resist poison: `1 carpentery_bench + 1 kitchen_bench + 2 anti-poison_pill`
- To resist cold: `1 thermos + 4 hot_coffee`

## Features

GNU readline provides a `TAB` completion, `^R` reverse search, `^L` clear screen, `↑↓` history search and so on.

```
> 1 biofuel_
biofuel_can               biofuel_deep-mining_drill biofuel_generator         biofuel_radar
biofuel_composter         biofuel_extractor         biofuel_lamp              biofuel_stove
> 1 biofuel_extractor + 1 biofuel_
biofuel_can               biofuel_deep-mining_drill biofuel_generator         biofuel_radar
biofuel_composter         biofuel_extractor         biofuel_lamp              biofuel_stove
> 1 biofuel_extractor + 1 biofuel_generator
===========================================
FABRICATOR
===========================================
1 biofuel_generator
-------------------------------------------
20 steel_ingot
20 steel_screw
12 electronics
 8 copper_ingot
 2 glass
===========================================
MACHINING BENCH
===========================================
20 steel_screw
12 electronics
 1 biofuel_extractor
-------------------------------------------
36 copper_ingot
24 epoxy
24 organic_resin
17 refined_gold
15 iron_ingot
10 copper_nail
 1 steel_ingot
===========================================
CONCRETE FURNACE
===========================================
21 steel_ingot
17 refined_gold
 2 glass
-------------------------------------------
34 gold_ore
21 steel_bloom
 2 silica_ore
===========================================
MORTAR AND PESTLE
===========================================
24 epoxy
24 organic_resin
21 steel_bloom
-------------------------------------------
126 iron_ore
 96 tree_sap
 48 sulfur
 24 oxite
 24 wood
 21 coal_ore
===========================================
96 tree_sap
-------------------------------------------
384 stick
===========================================
ANVIL BENCH
===========================================
10 copper_nail
-------------------------------------------
1 copper_ingot
===========================================
CHARACTER
===========================================
384 stick
-------------------------------------------
39 wood
===========================================
STONE FURNACE
===========================================
45 copper_ingot
15 iron_ingot
-------------------------------------------
90 copper_ore
30 iron_ore
===========================================
TOTAL RESOURCES
===========================================
1 biofuel_extractor
1 biofuel_generator
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
ValueError: biofuelextractor, biofuel_gen

Did you mean?
- biofuelextractor: biofuel_extractor, biofuel_generator, biofuel_radar
- biofuel_gen: biofuel_can, biofuel_generator, biofuel_stove
```

## Developers

### Visual Studio Code

To change command line arguments, edit `.vscode/launch.json` file and use either `Start Debugging (F5)` or `Run Without Debugging (Ctrl+F5)`. Include a property as follows `"program": "application.py"` to run the main entry point rather than current file in the editor.

Enable from the settings `Editor: Format On Save`.
