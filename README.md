# Icarus tool

The command line tool calculates total amount of resources and groups them by workstations. Tech tree has been updated after **Icarus week forty two update**.

## Getting started

Create a virtual environment and install dependencies before running the application.

### Windows

Powershell might not provide the same output as Bash shell. The reason remains unknown.

```
py -m venv .wenv
.wenv\Scripts\activate
python -m pip install pyreadline mypy black

python -m unittest
python -m mypy application.py calculator.py test_application.py test_calculator.py
python -m black *.py
python application.py -g data\tech_tree.txt
deactivate
```

### Linux

The `readline` package is most likely already installed as a dependency of Bash. Much like python should be pre-installed with the distribution. A creation of virtual environment is not necessary at all but here is how.

```
python -m venv .venv
source .venv/bin/activate
python -m pip install readline mypy black

python -m unittest
python -m mypy *.py
python -m black *.py
python application.py -g data/tech_tree.txt
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
amount name [+ amount name] [- amount name]
```

### Example

```
> 1 stone_furnace + 1 anvil_bench + 1 machining_bench - 10 epoxy
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
================================================================
ANVIL BENCH
================================================================
120 iron_nail
----------------------------------------------------------------
12 iron_ingot
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
STONE FURNACE
================================================================
92 iron_ingot
----------------------------------------------------------------
184 iron_ore
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
CHARACTER
================================================================
4 stick
----------------------------------------------------------------
1 wood
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
  0 sulfur
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

## Developers

A unit testing framework `unittest` and a static code analysis tool `mypy` proved to be very useful in the developing process. The source code formatter `black` makes visual styling decisions a trifling matter.

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

- Quick Open `(Ctrl+P)`

      ext install ms-python.python

- Command Palette `(Ctrl+Shift+P)`

      Python: Select Interpreter (./.venv/bin/python)
      Python: Configure Tests (unittest > Root directory > test_*.py)

- Settings `(Ctrl+,)`

      Testing: Automatically Open Peek View (never)
      Smart Scroll: Enabled (no)
      Formatting: provider (black)
      Editor: Format On Save (yes)
      Linting: Mypy Enabled (yes)

To change command line arguments, edit `.vscode/launch.json` file and use either `Start Debugging (F5)` or `Run Without Debugging (Ctrl+F5)`. Include a property as follows `"program": "application.py"` to run the main entry point rather than current file in the editor.

### Visual Studio Community

To change command line arguments, edit `Project > Properties > Debug > Script Arguments` field and use either `Start Debugging (F5)` or `Start Without Debugging (Ctrl+F5)`.

For me, there was a major problem detecting breakpoints when debugging test case with an infinite loop. Test explorer froze up effectively preventing any further testing.

## References

- [1] <https://wiki.archlinux.org/title/Snap#Classic_snaps>