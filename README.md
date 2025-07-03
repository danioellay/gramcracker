## gramcracker
An ASP-based Nonogram Solver & GUI

## Nonogram GUI
You can start the interactive GUI with 
> python -m gui

By default, this will open the _Nonogram Generator_ window, where you can create a black and white image that will be turned into a nonogram after pressing 'OK'.
Alternatively, you can specify a nonogram encoding file to load at the start, skipping the generator. Lastly, you can give the name of a solver to immediately solve the loaded nonogram. 
Example uses:
> python -m gui nonograms/example_04.txt
> 
> python -m gui nonograms/example_03.lp sbs-improved

### Manual Solving
Inside the _Nonogram GUI_, you can try to solve a nonogram manually by left-clicking on the cells. You can also mark cells by right-clicking them. 
By default, unsatisfied hints are emphasized in red. You can disable this in the 'View' menu.

### Automatic Solving
You can also use the computer to solve the nonogram for you with the 'Solver' menu. Here you can also enable uniqueness checking and have an option to find all solutions to a given nonogram.
If a solver found multiple solutions, you can cycle through them using Ctrl + H and Ctrl + J, or the 'View' menu.

### Nonogram Editing
You can change any row or column hint directly by clicking on it and entering a valid list of numbers, separated by spaces.
You can also fill the grid arbitrarily and then turn that grid into a nonogram by pressing Ctrl + Shift + N, or by using the 'File/New from current solution' menu option.
Resizing the nonogram is not supported, you need to use the _Nonogram Generator_ to create a new one. 

## Nonogram Generator
The _Nonogram Generator_ opens when you launch the application without parameters, or by pressing Ctrl + N from inside the _Nonogram GUI_.
Here you can create a nonogram yourself using the controls on the left hand side.
On the right hand side, you see a preview of the image encoded in your nonogram.

At the top of the left panel, you can adjust the grid size.
Then you can pick between three options:
1. An empty image (all white).
2. A randomly generated image - you can adjust the black-to-white ratio and how correlated neighbouring pixels are.
3. Load an image file and convert it to a nonogram - you can adjust the brightness threshold of the black and white image.

When you are happy with the preview on the right and the uniqueness properties of you nonogram, you can press OK (or hit 'Enter') to load it into the _Nonogram GUI_.
