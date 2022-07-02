## Getting started

Create a virtual environment and install dependencies before running the application.

### Windows

```
py -m venv .venv
.venv\Scripts\activate
python -m pip install pyreadline
python -m pip install pyinstaller

python -m unittest
python application.py

pyinstaller --onefile application.py
deactivate
dist\application.exe
```

### Linux

```
python -m venv .venv
source .venv/bin/activate
python -m pip install readline

python -m unittest
python application.py
deactivate
```

## Usage

```
.\application.py -i <inputfile> -gh
```

The command line arguments supported by the program are as follows:

```
-i --file=    A text file where each line contains an equation.
-h --help     Print manual at the beginning of the program.
-g --gnu      Apply GNU readline functionality to python's input.
```

The manual will be displayed and program waits for a text input.

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
> 1 bio
biofuel_can       biofuel_composter biofuel_extractor biofuel_generator
> 1 biofuel_extractor + 1 bio
biofuel_can       biofuel_composter biofuel_extractor biofuel_generator
> 1 biofuel_extractor + 1 biofuel_generator
-------------------------------------------
20 steel_ingot
20 steel_screw
15 iron_ingot
12 electronics
10 copper_nail
 8 copper_ingot
 5 refined_gold
 2 glass
-------------------------------------------
44 copper_ingot
30 iron_ore
24 epoxy
24 organic_resin
21 steel_ingot
17 refined_gold
 2 silica_ore
-------------------------------------------
96 tree_sap
88 copper_ore
48 sulfur
34 gold_ore
24 oxite
24 wood
21 steel_bloom
-------------------------------------------
384 stick
156 iron_ore
 21 coal_ore
-------------------------------------------
63 wood

TOTAL RESOURCES
-------------------------------------------
156 iron_ore
 88 copper_ore
 63 wood
 48 sulfur
 34 gold_ore
 24 oxite
 21 coal_ore
 10 copper_nail
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
