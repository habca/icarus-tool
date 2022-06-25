## Getting started

Create a virtual environment and install dependencies before running the application.

### Windows

```
py -m venv .venv
.venv\Scripts\activate
py -m pip install pyreadline
```

```
py -m unittest
py application.py
deactivate
```

### Linux

```
python -m venv .venv
source .venv/bin/activate
python -m pip install readline
```

```
python -m unittest
python application.py
deactivate
```

## Usage

GNU readline provides a `TAB` completion, `^R` reverse search `↑↓` history search to name a few.

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
