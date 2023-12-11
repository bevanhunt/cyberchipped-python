from .main import main
import os


def test_main():
    assert main() == "Hello there! How can I assist you today?"
    os.remove("cyberchipped.db")
