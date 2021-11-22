from fractions import Fraction
from babou.base import Surreal, ω


def test_frac_1_2():
    assert Surreal(2/4) == Surreal(1/2)


def test_le_1():
    assert Surreal(1/4) <= Surreal(2/8)


def test_frac_15_16_equiv_to_basic():
    equiv = Surreal(Surreal(7/8), Surreal(1))
    assert Surreal(15/16) == equiv


def test_frac_float():
    assert float(Surreal(Fraction(45, 16))) == float(Fraction(45, 16))


def test_int_float():
    assert float(Surreal(24)) == float(24)


def test_frac_int():
    assert int(Surreal(Fraction(3, 4))) == int(Fraction(3, 4))


def test_equiv_by_birthday_party_int():
    assert Surreal(2, 5) == Surreal(3)


def test_equiv_by_birthday_party_frac():
    assert Surreal(Fraction(2, 1), 5) == Surreal(3)


def test_one_third():
    assert isinstance(Surreal(1) / Surreal(3), Surreal)


def test_div_by_frac():
    assert isinstance(Surreal(1) / Surreal(Fraction(2, 3)), Surreal)


def test_omega_plus_one_equiv():
    assert ω + 1 == Surreal(ω, [])
