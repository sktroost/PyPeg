from pypeg.vm import run

def test_a():
    assert run('lpeg.P"a"', "a") is True
    assert run('lpeg.P"a"', "b") is None
