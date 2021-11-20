from babou.base import Surreal, BasicSurreal, ExplicitSurrealSet


def test_frac_1_2():
    assert Surreal(2/4) == Surreal(1/2)


def test_le_1():
    assert Surreal(1/4) <= Surreal(2/8)


def test_frac_15_16_equiv_to_basic():
    equiv = BasicSurreal(
            ExplicitSurrealSet([Surreal(7/8)]),
            ExplicitSurrealSet([Surreal(1)]))
    assert Surreal(15/16) == equiv
