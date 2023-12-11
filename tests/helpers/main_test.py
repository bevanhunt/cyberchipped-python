from .main import Planet, echo


def test_main():
    planet = Planet("Mars is a great place to visit!")
    assert planet.name == "Mars"
    assert planet.true
    assert not planet.false
    assert planet.number == 1
    assert (
        echo("Hello there! How can I assist you today?")
        == "Hello there! How can I assist you today?"
    )
