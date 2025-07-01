## gramcracker
An ASP-based Nonogram Solver & GUI

## Nonogram GUI
You can start the interactive GUI with 
> python -m gui

By default, this will open the _Nonogram Generator_ window, where you can create a black and white image that will be turned into a nonogram after pressing 'OK'.
Alternatively, you can specify a nonogram encoding file to load at the start, skipping the generator. Lastly, you can give the name of a solver to immediately solve the loaded nonogram. 
Example uses:
> python -m gui nonograms/example_04c.lp
> 
> python -m gui nonograms/example_05.lp sbs-improved

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
