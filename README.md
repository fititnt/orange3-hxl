# HXL visual ETL (Orange3 add-on)

This is an early draft of [Orange3](http://orange.biolab.si) add-on with minimal
awareness of data labeled with [HXL](https://hxlstandard.org/).

## Features

### Data Vault Conf
[WORKING DRAFT] Configure active local data vault configurations. This allows overriding defaults.

### Download Raw File

Download remote resource into a local FileRAW

### Unzip Raw File
[WORKING DRAFT] Unzip (zip, gzip, bzip, ...) an FileRAW into an FileRAWCollection

### Select Raw File
[DRAFT] From a local FileRAWCollection, select an FileRAW

### Load Raw File
Convert a local FileRAW into Orange3 Data / DataFrame.
Required to allow use with other widgets.

Supported features (*):

- `pandas.read_table`
- `pandas.read_csv`
- `pandas.read_excel`
- `pandas.read_feather`
- `pandas.read_fwf`
- `pandas.read_html`
- `pandas.read_json`
- `pandas.json_normalize`
- `pandas.read_orc`
- `pandas.read_parquet`
- `pandas.read_sas`
- `pandas.read_spss`
- `pandas.read_stata`
- `pandas.read_xml`

_(*) Some features will require additional python packages which are not installed by default with this add-on. The user will be warned about this._

### Statistical Role

Change statistical role (the "feature", "target", "meta", "ignore")
using HXL patterns instead of stric exact names for the data variables.

### Data Type

[DRAFT] Change the computational data type (the "numeric", "categorical" "text", "datetime") using HXL patterns instead of stric exact names for the data variables.

### HXL short names

[EARLY DRAFT] Make HXLated input data with shorter variable names.

### RAW Info
[DRAFT] Inspect a FileRAW or FileRAWCollection


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

<!--

@TODO use this as JSON example input https://vocabulary.unocha.org/json/beta-v4/countries.json
@TODO this is excel, not sure if we enable without HXProxy https://docs.google.com/spreadsheets/d/1NjSI2LaS3SqbgYc0HdD8oIb7lofGtiHgoKKATCpwVdY/edit#gid=1088874596
      https://proxy.hxlstandard.org/data.csv?dest=data_edit&filter01=cut&cut-skip-untagged01=on&strip-headers=on&force=on&url=https%3A%2F%2Fdocs.google.com%2Fspreadsheets%2Fd%2F1NjSI2LaS3SqbgYc0HdD8oIb7lofGtiHgoKKATCpwVdY%2Fedit%23gid%3D1088874596

@TODO CSV
-->