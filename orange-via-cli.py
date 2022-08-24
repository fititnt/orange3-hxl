#!/usr/bin/env python3

# Run with
#     pytest --capture=no -vvvv ./orange-via-cli.py

# @example https://github.com/mkinney/pytest-qt-example
# @see https://docs.pytest.org/en/6.2.x/customize.html

# pytest -W ignore::DeprecationWarning -W ignore::RuntimeWarning ./orange-via-cli.py
# 

# pytest -c /workspace/git/fititnt/orange3-hxl/pytest.ini /home/fititnt/.local/lib/python3.8/site-packages/Orange/canvas/__main__.py

# orange-canvas --no-welcome --no-splash --log-level=4 /workspace/git/EticaAI/lsf-orange-data-mining/teste-remoto-HXLvisualETL__v2-worldbank-funcionando.temp.ows

# pytest -c tox.ini ./orange-via-cli.py
# orange-canvas --no-welcome --no-splash --log-level=4

# pip install pytest-qt
# pip install pytest-bdd
import sys
import pytest

from Orange.canvas.__main__ import main
from Orange.canvas.__main__ import OMain

# import os
# import sys
import pytest

# from PyQt5 import QtGui, QtCore, QtWidgets, QtTest
# from PyQt5.QtWidgets import *
# from PyQt5.QtCore import QCoreApplication, Qt, QObject

# from AnyQt.QtCore import (
#     QAbstractTableModel,
#     QEvent,
#     QItemSelectionModel,
#     QModelIndex,
#     Qt,
# )
from pytestqt.qt_compat import qt_api
from pytestqt.plugin import QtBot

# def test_screenshot(qtbot):
#     button = qt_api.QtWidgets.QPushButton()
#     button.setText("Hello World!")
#     qtbot.add_widget(button)
#     path = qtbot.screenshot(button)
#     assert False, path  # show the path and fail the test

# def test_hello(qtbot):
#     """test clicking changes a label"""
#     print('before  init widget')

#     # widget = OMain().run(['--no-welcome', '--no-splash', '--log-level', '4'])
#     widget = OMain()
#     print(widget)
#     # widget.run(['--no-welcome', '--no-splash', '--log-level', '4'])
#     # widget.run(['--no-splash'])
#     # widget.run(['--no-welcome','--no-splash','--log-level=4'])
#     # widget.run(['--no-welcome', '--no-splash'])
#     # widget.run(['--no-welcome', '--no-splash', '/workspace/git/EticaAI/lsf-orange-data-mining/teste-remoto-HXLvisualETL__v2-worldbank-funcionando.temp.ows'])
#     widget.run(['--no-welcome', '--no-splash', '/workspace/git/EticaAI/lsf-orange-data-mining/orange-simple-test.temp.ows'])
#     print('after init widget')

#     assert True, True

# def test_hello_v2(qtbot: QtBot):
#     """test clicking changes a label"""

#     print('before  init widget')

#     # widget = OMain().run(['--no-welcome', '--no-splash', '--log-level', '4'])
#     print('before "widget = OMain()"')
#     widget = OMain()
#     print(widget)
#     print('before "widget.run([\'--no-welcome\' ..."')
#     widget.run(['--no-welcome', '--no-splash', '/workspace/git/EticaAI/lsf-orange-data-mining/orange-simple-test.temp.ows'])
#     print('after "widget.run([\'--no-welcome\' ..."')
#     qtbot.addWidget(widget)
#     print('after init widget')
#     # print(widget)
#     # raise Exception(widget)

#     assert True, True

def test_hello_v2b(qtbot: QtBot):
    # This one will open Orange3 gui, but does not release way to
    # qbot "see" the windows
    return None

    print('before  init widget')

    # widget = OMain().run(['--no-welcome', '--no-splash', '--log-level', '4'])
    print('before "widget = OMain()"')
    widget = OMain()
    print(widget)
    print('before "widget.run([\'--no-welcome\' ..."')
    with widget.run(['--no-welcome', '--no-splash', '--log-level', '4', '/workspace/git/EticaAI/lsf-orange-data-mining/orange-simple-test.temp.ows']) as runner:
        print('inside runner')
        pass
    print('after "widget.run([\'--no-welcome\' ..."')
    qtbot.addWidget(widget)
    print('after init widget')
    # print(widget)
    # raise Exception(widget)

    assert True, True

def test_hello_v2b2(qtbot: QtBot):
    # This one will open Orange3 gui, but does not release way to
    # qbot "see" the windows

    print('before  init widget')

    # widget = OMain().run(['--no-welcome', '--no-splash', '--log-level', '4'])
    print('before "widget = OMain()"')
    widget = OMain()
    print(widget)
    print('before "widget.run([\'--no-welcome\' ..."')
    with widget.run(['--no-welcome', '--no-splash', '--log-level', '4', '/workspace/git/EticaAI/lsf-orange-data-mining/orange-simple-test.temp.ows']) as runner:
        print('inside runner')
        pass
    print('after "widget.run([\'--no-welcome\' ..."')
    qtbot.addWidget(widget)
    print('after init widget')
    # print(widget)
    # raise Exception(widget)

    # @see https://code-maven.com/python-timeout

    assert True, True

# def test_hello_v3(qtbot: QtBot):
#     """test clicking changes a label"""

#     print('before  init widget')

#     # widget = OMain().run(['--no-welcome', '--no-splash', '--log-level', '4'])
#     qapp = OMain()
#     print('after qapp = OMain()')
#     qapp.setup_application()
#     print('after qapp.setup_application()')
#     qapp.setup_sys_redirections()
#     print('after qapp.setup_sys_redirections()')
#     qapp.setup_logging()
#     print('after qapp.setup_logging()')
#     main_windown = qapp.create_main_window()
#     print('after qapp.create_main_window()')
#     qtbot.addWidget(main_windown)
#     # print(qapp)
#     # print(qtbot)
#     # qapp.run(['--no-welcome', '--no-splash', '/workspace/git/EticaAI/lsf-orange-data-mining/orange-simple-test.temp.ows'])
#     # qtbot.addWidget(widget)
#     print('after init widget')
#     # print(widget)
#     # raise Exception(widget)

#     assert True, True
