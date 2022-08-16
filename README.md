# Orange3 HXL visual ETL add-on

This is an early draft of [Orange3](http://orange.biolab.si) add-on with minimal
awareness of data labeled with [HXL](https://hxlstandard.org/).

<!--
This is an example add-on for [Orange3](http://orange.biolab.si). Add-on can extend Orange either 
in scripting or GUI part, or in both. We here focus on the GUI part and implement a simple (empty) widget,
register it with Orange and add a new workflow with this widget to example tutorials.
-->

## Installation

To install the add-on from source run

    pip install .

To register this add-on with Orange, but keep the code in the development directory (do not copy it to 
Python's site-packages directory), run

    pip install -e .

Documentation / widget help can be built by running

    make html htmlhelp

from the doc directory.

## Usage


After the installation, the widget from this add-on is registered with Orange. To run Orange from the terminal,
use

    orange-canvas

or

    python -m Orange.canvas

The new widget appears in the toolbox bar under the section Example.

![screenshot](https://raw.githubusercontent.com/biolab/orange3-example-addon/master/screenshot.png)


## TODOs

- https://github.com/fititnt/orange3-hxl/issues/1
- (...)

<!--
orange-canvas --no-welcome --no-splash

pip install orange3 Orange3-Geo Orange3-Timeseries orange3-text
pip install Orange3-Survival-Analysis

## To re-install later all the things
pip uninstall Orange3-HXLvisualETL orange3 Orange3-Geo Orange3-Timeseries orange3-text Orange3-Survival-Analysis Orange3-WorldHappiness Orange3-Explain
-->