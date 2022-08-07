#!/usr/bin/env python3

# @example https://github.com/mkinney/pytest-qt-example

# pytest ./orange-via-cli.py
# pytest -W ignore::DeprecationWarning -W ignore::RuntimeWarning ./orange-via-cli.py

# pip install pytest-qt
# pip install pytest-bdd
import pytest

from Orange.canvas.__main__ import main

import os
import sys
import pytest

from PyQt5 import QtGui, QtCore, QtWidgets, QtTest
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QCoreApplication, Qt, QObject

from pytestqt.plugin import QtBot


def test_hello(qtbot):
    """test clicking changes a label"""
    widget = main()
    qtbot.addWidget(widget)

    # click in the Greet button and make sure it updates the appropriate label
    # qtbot.mouseClick(widget.button_greet, qt_api.QtCore.Qt.MouseButton.LeftButton)

    # assert widget.greet_label.text() == "Hello!"
