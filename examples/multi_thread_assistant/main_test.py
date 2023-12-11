from .main import main
from unittest.mock import patch


def test_main():
    with patch("builtins.print") as mocked_print:
        main()
        mocked_print.assert_called_once_with("Hello there! How can I assist you today?")
