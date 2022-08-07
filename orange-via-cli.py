#!/usr/bin/env python3

# pytest ./orange-via-cli.py
# pytest -W ignore::DeprecationWarning ./orange-via-cli.py

# pip install pytest-qt
# pip install pytest-bdd
import pytest

from Orange.canvas.__main__ import main

class Fruit:
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return self.name == other.name


@pytest.fixture
def my_fruit():
    return Fruit("appleqq")


@pytest.fixture
def fruit_basket(my_fruit):
    return [Fruit("banana"), my_fruit]


def test_my_fruit_in_basket(my_fruit, fruit_basket):
    assert my_fruit in fruit_basket