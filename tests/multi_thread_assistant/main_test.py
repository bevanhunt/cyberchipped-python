from .main import main
import os


def test_main():
    assert main() == "The result of adding 1 and 1 together is 2."
    os.remove("cyberchipped.db")
