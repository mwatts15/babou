"""Implementations for dyadic rational surreal numbers in canonical form.

A surreal number represents a dyadic rational if and only if it has a finite
birthday.
"""

from fractions import Fraction
import numbers
import operator

from . import base


def is_dyadic(fraction):
    den = abs(fraction.denominator)
    return not (den & (den - 1))


def _is_power_of_2(val):
    return not (val & (val - 1))


class DyadicSurreal(base.Surreal, numbers.Rational):
    """ABC for a dyadic rational Surreal number in canonical form."""

    def birthday_finite(self):
        return True

    def is_finite(self):
        return True

    def is_infinite(self):
        return False

    def is_infinitesimal(self):
        return False

    def is_real(self):
        return True

    def is_rational(self):
        return True

    def is_dyadic(self):
        return True


class IntegerSurreal(DyadicSurreal, numbers.Integral):
    """An integer surreal number in canonical form.

    :param int intval: Any object convertable to an integer.
    """

    def __init__(self, value=0):
        self._value = int(value)
        self._left = None
        self._right = None

    def __int__(self):
        return self._value

    def is_integral(self):
        return True

    def birthday(self):
        return abs(self._value)

    @property
    def left(self):
        if self._left is None:
            if self._value > 0:
                self._left = base.ExplicitSurrealSet([self._value - 1])
            else:
                self._left = base.EmptySurrealSet()

        return self._left

    @property
    def right(self):
        if self._right is None:
            if self._value < 0:
                self._right = base.ExplicitSurrealSet([self._value + 1])
            else:
                self._right = base.EmptySurrealSet()

        return self._right

    def simple_repr(self):
        return str(self._value)

    def _binary_op(self, opname, other, swap=False):

        if isinstance(other, IntegerSurreal):
            other = other._value

        elif isinstance(other, base.Surreal):
            return getattr(super(), opname)(other)

        elif not isinstance(other, int):
            return NotImplemented

        op = getattr(operator, opname)

        if swap:
            result = op(other, self._value)

        else:
            result = op(self._value, other)

        if isinstance(result, int):
            return IntegerSurreal(result)
        else:
            return result

    def __eq__(self, other): return self._binary_op('__eq__', other)

    def __le__(self, other): return self._binary_op('__le__', other)

    def __lt__(self, other): return self._binary_op('__lt__', other)

    def __ge__(self, other): return self._binary_op('__ge__', other)

    def __gt__(self, other): return self._binary_op('__gt__', other)

    def __add__(self, other): return self._binary_op('__add__', other)

    def __radd__(self, other): return self._binary_op('__add__', other, True)

    def __and__(self, other): return self._binary_op('__and__', other)

    def __rand__(self, other): return self._binary_op('__and__', other, True)

    def __floordiv__(self, other): return self._binary_op('__floordiv__', other)

    def __rfloordiv__(self, other): return self._binary_op('__floordiv__', other, True)

    def __lshift__(self, other): return self._binary_op('__lshift__', other)

    def __rlshift__(self, other): return self._binary_op('__lshift__', other, True)

    def __mod__(self, other): return self._binary_op('__mod__', other)

    def __rmod__(self, other): return self._binary_op('__mod__', other, True)

    def __mul__(self, other): return self._binary_op('__mul__', other)

    def __rmul__(self, other): return self._binary_op('__mul__', other, True)

    def __or__(self, other): return self._binary_op('__or__', other)

    def __ror__(self, other): return self._binary_op('__or__', other, True)

    def __pow__(self, other): return self._binary_op('__pow__', other)

    def __rpow__(self, other): return self._binary_op('__pow__', other, True)

    def __rshift__(self, other): return self._binary_op('__rshift__', other)

    def __rrshift__(self, other): return self._binary_op('__rshift__', other, True)

    def __sub__(self, other): return self._binary_op('__sub__', other)

    def __rsub__(self, other): return self._binary_op('__sub__', other, True)

    def __truediv__(self, other):
        if isinstance(other, numbers.Integral):
            intval = int(other)
            if _is_power_of_2(intval):
                return DyadicFractionSurreal(Fraction(self._value, intval))
        elif isinstance(other, numbers.Rational):
            if _is_power_of_2(other.numerator):
                return DyadicFractionSurreal(Fraction(self._value, other))

        return self._binary_op('__truediv__', other)

    def __rtruediv__(self, other): return self._binary_op('__truediv__', other, True)

    def __xor__(self, other): return self._binary_op('__xor__', other)

    def __rxor__(self, other): return self._binary_op('__xor__', other, True)

    def __abs__(self): return IntegerSurreal(self._value.__abs__())

    def __invert__(self): return IntegerSurreal(self._value.__invert__())

    def __neg__(self): return IntegerSurreal(self._value.__neg__())

    def __pos__(self): self

    def __ceil__(self): return self

    def __floor__(self): return self

    def __round__(self, *args): return IntegerSurreal(round(self._value, *args))

    def __trunc__(self): return self

    def __float__(self):
        return float(self._value)

    def __bool__(self):
        return self._value.__bool__()


class DyadicFractionSurreal(DyadicSurreal, numbers.Rational):
    def __init__(self, value):
        if not is_dyadic(value):
            raise ValueError('Given fraction is not dyadic')
        self._value = value
        self._left = None
        self._right = None

    @property
    def numerator(self):
        return self._value.numerator

    @property
    def denominator(self):
        return self._value.denominator

    @property
    def left(self):
        if self._left is None:
            self._left = base.ExplicitSurrealSet([
                DyadicFractionSurreal(
                    Fraction(self._value.numerator - 1, self._value.denominator))])
        return self._left

    @property
    def right(self):
        if self._right is None:
            self._right = base.ExplicitSurrealSet([
                DyadicFractionSurreal(
                    Fraction(self._value.numerator + 1, self._value.denominator))])
        return self._right

    def simple_repr(self):
        return repr(self._value)

    def _binary_op(self, opname, other, swap=False):

        if isinstance(other, DyadicFractionSurreal):
            other = other._value

        elif isinstance(other, base.Surreal):
            return getattr(super(), opname)(other)

        elif not isinstance(other, Fraction):
            return NotImplemented

        op = getattr(operator, opname)

        if swap:
            result = op(other, self._value)
        else:
            result = op(self._value, other)

        if isinstance(result, bool):
            return result
        elif isinstance(result, numbers.Number):
            try:
                return base.Surreal(result)
            except TypeError:
                return result
        return result

    def __eq__(self, other): return self._binary_op('__eq__', other)

    def __le__(self, other): return self._binary_op('__le__', other)

    def __ge__(self, other): return self._binary_op('__ge__', other)

    def __lt__(self, other):
        surreal_set = None
        if isinstance(other, base.SurrealSet):
            surreal_set = other
        elif isinstance(other, base.Surreal) and isinstance(other.left, base.SurrealSet):
            surreal_set = other.left

        if surreal_set is not None:
            for item in surreal_set:
                if (isinstance(item, DyadicFractionSurreal) or
                        isinstance(item, IntegerSurreal)):
                    if self._value <= item._value:
                        return True
        return self._binary_op('__lt__', other)

    def __gt__(self, other):
        surreal_set = None
        if isinstance(other, base.SurrealSet):
            surreal_set = other
        elif isinstance(other, base.Surreal) and isinstance(other.left, base.SurrealSet):
            surreal_set = other.right

        if surreal_set is not None:
            for item in surreal_set:
                if (isinstance(item, DyadicFractionSurreal) or
                        isinstance(item, IntegerSurreal)):
                    if self._value >= item._value:
                        return True
        return self._binary_op('__gt__', other)

    def __add__(self, other): return self._binary_op('__add__', other)

    def __radd__(self, other): return self._binary_op('__add__', other, True)

    def __and__(self, other): return self._binary_op('__and__', other)

    def __rand__(self, other): return self._binary_op('__and__', other, True)

    def __floordiv__(self, other): return self._binary_op('__floordiv__', other)

    def __rfloordiv__(self, other): return self._binary_op('__floordiv__', other, True)

    def __lshift__(self, other): return self._binary_op('__lshift__', other)

    def __rlshift__(self, other): return self._binary_op('__lshift__', other, True)

    def __mod__(self, other): return self._binary_op('__mod__', other)

    def __rmod__(self, other): return self._binary_op('__mod__', other, True)

    def __mul__(self, other): return self._binary_op('__mul__', other)

    def __rmul__(self, other): return self._binary_op('__mul__', other, True)

    def __or__(self, other): return self._binary_op('__or__', other)

    def __ror__(self, other): return self._binary_op('__or__', other, True)

    def __pow__(self, other): return self._binary_op('__pow__', other)

    def __rpow__(self, other): return self._binary_op('__pow__', other, True)

    def __rshift__(self, other): return self._binary_op('__rshift__', other)

    def __rrshift__(self, other): return self._binary_op('__rshift__', other, True)

    def __sub__(self, other): return self._binary_op('__sub__', other)

    def __rsub__(self, other): return self._binary_op('__sub__', other, True)

    def __truediv__(self, other): return self._binary_op('__truediv__', other)

    def __rtruediv__(self, other): return self._binary_op('__truediv__', other, True)

    def __abs__(self):
        return DyadicFractionSurreal(self._value.__abs__())

    def __neg__(self):
        return DyadicFractionSurreal(self._value.__neg__())

    def __pos__(self): self

    def __ceil__(self):
        return IntegerSurreal(self._value.__ceil__())

    def __floor__(self):
        return IntegerSurreal(self._value.__floor__())

    def __round__(self, *args):
        return IntegerSurreal(round(self._value, *args))

    def __trunc__(self):
        return IntegerSurreal(self._value.__trunc__())

    def __float__(self):
        return float(self._value)

    def is_integral(self):
        return self._value.denominator == 1

    def birthday(self):
        return abs(self._value)


class DyadicsType(base.SurrealSet):
    '''
    The set of all surreal numbers generated in some finitely indexed generation
    '''
    def birthday_finite(self):
        return True

    def is_finite(self):
        return False

    def largest(self):
        return None

    def smallest(self):
        return None

    def inner_repr(self, maxlen=None):
        # XXX: dunno what the right representation is for this, just took it from
        # Wikipedia
        return "S*"

    def __contains__(self, item):
        if isinstance(item, base.Surreal) and item.is_dyadic():
            return True
        return False

    def __lt__(self, other):
        if isinstance(other, base.OmegaType):
            return False
        elif isinstance(other, DyadicSurreal):
            return False
        elif isinstance(other, base.Surreal):
            # if there's an element in the left of other that is greater than this than
            # return True. Basically, if it's Omega, that'll do...
            if base.OMEGA in other.left:
                return True
        return NotImplemented


DYADICS = DyadicsType()
