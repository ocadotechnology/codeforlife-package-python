## Creating a graph of models

The library <i>django-extensions</i> allows Django to plot current models structure as a series of graphs.

To run this feature make sure you have installed all the dependencies by running:
```bash
pipenv install --dev
```
and that you are in a virtual environment by running:
```bash
pipenv shell
```

Then make sure you are in the root of the project and run the following command:
```bash
python manage.py graph_models --pydot -a -g- o docs/project.png
```

This will generate a png file with a graphed models, you can also run generate editable <i>dot</i> files that can be edited using a tool such as <i>xdot</i> using the following command:
```bash
python manage.py graph_models --pydot -a -g -o docs/project.dot
```

Finally you can also select different parts of project to plot, try using:
```bash
python manage.py graph_models --pydot user -g -o project.dot
```
to only show the user app being graphed.