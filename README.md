# HXL visual ETL (Orange3 add-on)
[![GitHub](https://img.shields.io/badge/GitHub-fititnt%2Forange3--hxl-lightgrey?logo=github&style=social[fititnt/orange3-hxl] "GitHub")](https://github.com/fititnt/orange3-hxl)
[![Pypi: Orange3-HXLvisualETL](https://img.shields.io/badge/python%20pypi-Orange3--HXLvisualETL-brightgreen[Python] 
 "Pypi: Orange3-HXLvisualETL")](https://pypi.org/project/Orange3-HXLvisualETL)

This is an early draft of [Orange3](http://orange.biolab.si) add-on with minimal
awareness of data labeled with [HXL](https://hxlstandard.org/).

To install this package, use

```bash
pip install Orange3-HXLvisualETL
```

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

### From Pypi (recommended)

    pip install Orange3-HXLvisualETL

### From source

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


<!--
## TODOs

- https://github.com/fititnt/orange3-hxl/issues/1
- https://realpython.com/python-pyqt-qthread/
- (...)

-->
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

>>> orange-canvas-cli.sh

# Whatever was exit status of main_loop(), we will leave unchanged.
# However likely critical errors will returno non-zero result

# ./orange-canvas-cli.sh /workspace/git/EticaAI/lsf-orange-data-mining/orange-simple-test.temp.ows

# ORANGECLI_DEBUG=1 ORANGECLI_USEXVFB=1 ./orange-canvas-cli.sh /workspace/git/EticaAI/lsf-orange-data-mining/orange-simple-test.temp.ows
# ORANGECLI_DEBUG=1 ORANGECLI_USEXVFB=1 ./orange-canvas-cli.sh /workspace/git/EticaAI/lsf-orange-data-mining/orange-simple-test.temp.ows /workspace/git/EticaAI/lsf-orange-data-mining/999999/0/iris.csv

#### Etc _______________________________________________________________________
## Discussions related to run orange via cli
# @see https://github.com/biolab/orange3/issues/1341
# @see https://github.com/biolab/orange3/issues/3874
# @see https://github.com/biolab/orange3/issues/4910
# @see https://github.com/biolab/orange3/pull/4966
# @see https://github.com/biolab/orange3/issues/2525

## Kill program after some time

# @see https://unix.stackexchange.com/questions/483879/stop-kill-a-process-from-the-command-line-after-a-certain-amount-of-time

## Xvfb related
# @see https://unix.stackexchange.com/questions/512356/is-there-any-way-to-launch-gui-application-without-gui

# @see https://discourse.nixos.org/t/running-qt-applications-with-xvfb-run/1696
# @see https://stackoverflow.com/questions/13215120/how-do-i-make-python-qt-and-webkit-work-on-a-headless-server

-->
