"""Base classes for surreal numbers and sets of them."""

from abc import ABCMeta, abstractmethod, abstractproperty
from collections.abc import Container, Set
import numbers
from itertools import islice
from fractions import Fraction


class TransfiniteError(RuntimeError):
    """
    Raised when an operation is attempted that may take an infinite number of
    steps, such as comparing two infinite sets.
    """


def surreal_binary_op(method):
    """Decorator for binary op methods on surreal numbers.

    Wraps the method and first attempts to convert the second argument to an
    instance of :class:`.Surreal` with :meth:`.Surreal.convert`. If that fails
    (raises a :exc:`TypeError`) ``NotImplemented`` is returned. Otherwise calls
    the wrapped method with the converted argument and returns that value.
    """

    def wrapper(self, other):
        if not isinstance(other, Surreal):
            try:
                other = Surreal(other)
            except TypeError:
                return NotImplemented

        return method(self, other)

    return wrapper


class SurrealMeta(ABCMeta):
    """This is a hack to create a nice general-purpose constructor for Surreal.
    """

    def __call__(cls, *args, **kwargs):
        if cls is Surreal:

            if len(args) == 0:
                return Surreal.convert(0)

            elif len(args) == 1:
                return Surreal.convert(args[0])

            elif len(args) == 2:
                return BasicSurreal(*args)

            else:
                raise TypeError('Constructor takes between 0 and 2 positional arguments')

        else:
            instance = object.__new__(cls, *args, **kwargs)
            instance.__init__(*args, **kwargs)
            return instance


class Surreal(numbers.Number, metaclass=SurrealMeta):
    """ABC for a surreal number.

    More properly this is a surreal number form, a pair of sets L and R
    of additional surreal numbers. Two surreal number forms may represent the
    same surreal number, in which case they are equivalent.

    The form is numeric, in that it represents a valid surreal number. This
    means every element of the right set is greater than every element of the
    left set.

    This class may be called like a constructor to create a new surreal number,
    which will be of the correct type given the arguments:

        * If called with no arguments will return surreal zero.
        * If called with a single argument will return that argument converted
          to a surreal with    :meth:`convert`.
        * When called with two arguments will return a surreal with    those
          arguments as left/right sets.

    .. attribute:: left

        Left :class:`.SurrealSet` of form.

    .. attribute:: right

        Right :class:`.SurrealSet` of form.
    """

    @abstractproperty
    def left(self):
        pass

    @abstractproperty
    def right(self):
        pass

    @abstractmethod
    def birthday(self):
        """
        An ordinal number indicating how many times the surreal number
        construction rules must be applied inductively to generate this number.

        The birthday of 0 is 0. All integer and dyadic rational surreals have
        positive finite birthdays, all others have infinite birthdays.

        If the birthday is finite a Python :class:`int` should be returned.
        Otherwise an infinite ordinal in the form of a :class:`.Surreal` may be
        returned, or ``None`` as a form of "I don't know."
        """
        pass

    @abstractmethod
    def birthday_finite(self):
        """If the birthday of this number is finite.

        This always returns a proper boolean value, even if the exact birthday
        cannot be determined.

        :rtype: bool
        """
        pass

    @abstractmethod
    def is_finite(self):
        """
        True if both :meth:`is_infinite` and :meth:`is_infinitesimal` return
        False.

        :rtype: bool
        """
        pass

    @abstractmethod
    def is_infinite(self):
        """
        True if the surreal number represented is infinite (i.e., absolute value
        larger than any real number).

        :rtype: bool
        """
        pass

    @abstractmethod
    def is_infinitesimal(self):
        """
        If the surreal number represented is infinitesimal (i.e., absolute
        value greater than zero but less than any real number).

        :rtype: bool
        """
        pass

    @abstractmethod
    def is_real(self):
        """True if the form represents a real number.

        :rtype: bool
        """
        pass

    @abstractmethod
    def is_rational(self):
        """True if the form represents a rational number.


        :rtype: bool
        """
        pass

    @abstractmethod
    def is_dyadic(self):
        """
        True if the form represents a dyadic number (rational where the
        denominator is a power of two).

        :rtype: bool
        """
        pass

    @abstractmethod
    def is_integral(self):
        """True if the form represents an integer.

        :rtype: bool
        """
        pass

    def simple_repr(self):
        """Simple text-based representation of the number represented by the form.

        This is mainly used for the text representation of elements in a
        :class:`.SurrealSet`.

        :rtype: str
        """
        return '?'

    def full_repr(self):
        """Full text representation of left and right sets in form {...|...}.

        :rtype: str.
        """
        return '{{{}|{}}}'.format(self.left.inner_repr(), self.right.inner_repr())

    def __repr__(self):
        return self.full_repr()

    @staticmethod
    def convert(value):
        """Convert a Python object into a surreal number of the appropriate type.

        :param value: Any builtin numeric type, or a string.
        :rtype: .Surreal
        """
        if isinstance(value, Surreal):
            return value

        elif isinstance(value, int):
            return Surreal.from_int(value)

        elif isinstance(value, float):
            return Surreal.from_float(value)

        elif isinstance(value, str):
            return Surreal.from_string(value)
        elif isinstance(value, Fraction):
            return Surreal.from_fraction(value)
        else:
            raise TypeError(
                "Don't know how to convert {} to Surreal"
                .format(type(value))
            )

    @staticmethod
    def from_int(value):
        """Convert a Python integer to a surreal number.

        :param int value: Integer value.
        :rtype: .Surreal
        """
        from .dyadic import IntegerSurreal
        return IntegerSurreal(value)

    @staticmethod
    def from_float(value):
        """Convert a Python float to a surreal number.

        :param float value: Float value.
        :rtype: .Surreal
        """
        value = float(value)
        if value.is_integer():
            return Surreal.from_int(value)
        else:
            return Surreal.from_fraction(Fraction(value))

    @staticmethod
    def from_fraction(value):
        if value.denominator == 1:
            return Surreal.from_int(value.numerator)
        from .dyadic import DyadicFractionSurreal, is_dyadic
        if is_dyadic(value):
            return DyadicFractionSurreal(value)
        else:
            raise NotImplementedError(f"only dyadic fractions supported, not {value}")

    @staticmethod
    def from_string(value):
        """Parse a string to a surreal number.

        :param int value: String representation of number.
        :rtype: .Surreal
        """
        raise NotImplementedError()

    def __bool__(self):
        return self != 0

    @surreal_binary_op
    def __eq__(self, other):
        if other is self:
            return True

        return self <= other and other <= self

    @surreal_binary_op
    def __le__(self, other):
        return self.left < other and self < other.right

    @surreal_binary_op
    def __ge__(self, other):
        return other <= self

    @surreal_binary_op
    def __lt__(self, other):
        return self <= other and not other <= self

    @surreal_binary_op
    def __gt__(self, other):
        return other <= self and not self <= other

    def __neg__(self):
        return BasicSurreal(-self.right, -self.left)

    @surreal_binary_op
    def __add__(self, other):
        return BasicSurreal(
            (self.left + other) | (self + other.left),
            (self.right + other) | (self + other.right),
        )

    @surreal_binary_op
    def __sub__(self, other):
        return BasicSurreal(
            (self.left - other) | (self - other.right),
            (self.right - other) | (self - other.left),
        )


class OmegaType(Surreal):
    def __init__(self, sign=1):
        if sign not in (-1, 1):
            raise ValueError('sign must be -1 or 1')
        self._sign = sign

    def is_infinite(self):
        return True

    def birthday(self):
        return OMEGA

    @property
    def left(self):
        from .dyadic import DYADICS
        if self._sign > 0:
            return DYADICS
        else:
            return EmptySurrealSet()

    def is_integral(self):
        return False

    def is_real(self):
        return False

    @property
    def right(self):
        from .dyadic import DYADICS
        if self._sign > 0:
            return EmptySurrealSet()
        else:
            return DYADICS

    def is_dyadic(self):
        '''
        ω is not reachable by finite induction, so it is not dyadic
        '''
        return False

    def simple_repr(self):
        return f'{self._sign<0 and "-" or ""}ω'

    def birthday_finite(self):
        return False

    def is_finite(self):
        return False

    def is_infinitesimal(self):
        return False

    def is_rational(self):
        return False

    def __add__(self, other):
        if isinstance(other, numbers.Integral):
            return OmegaPlusInteger(other)
        raise NotImplementedError('Only addition of integers to ω is supported')

    def __neg__(self):
        if self._sign > 0:
            return NEGATIVE_OMEGA
        else:
            return OMEGA


class OmegaPlusInteger(Surreal):
    '''
    Omega plus an integer
    '''
    # There may be a more generic ω + X to do here, but I don't know how to do that yet
    def __init__(self, addend):
        if addend == 0:
            raise ValueError("OmegaPlusInteger is for non-zero integers")
        self._addend = addend

    @property
    def left(self):
        if self._addend == 1:
            return ExplicitSurrealSet(OMEGA)
        elif self._addend > 1:
            return ExplicitSurrealSet(
                    OmegaPlusInteger(self._addend - 1))
        elif self._addend == -1:
            from .dyadic import DYADICS
            return DYADICS
        else:
            return ExplicitSurrealSet(
                    OmegaPlusInteger(self._addend + 1))

    @property
    def right(self):
        if self._addend == -1:
            return ExplicitSurrealSet(OMEGA)
        elif self._addend >= 1:
            return EmptySurrealSet()
        else:
            return ExplicitSurrealSet(
                    OmegaPlusInteger(self._addend + 1))

    def birthday(self):
        if self._addend > 0:
            return self
        else:
            return OmegaPlusInteger(-self._addend)

    def is_dyadic(self):
        return False

    def birthday_finite(self):
        return False

    def is_finite(self):
        return False

    def is_infinite(self):
        return True

    def is_integral(self):
        return False

    def is_rational(self):
        return False

    def is_real(self):
        return False

    def is_infinitesimal(self):
        return False


OMEGA = ω = OmegaType()
NEGATIVE_OMEGA = OmegaType(-1)


class SurrealSet(Container):
    """ABC for a (possibly infinite) immutable set of surreal numbers.

    Corresponds to the left or right side of {L|R} surreal forms.
    """

    @abstractmethod
    def is_finite(self):
        """If the set contains a finite number of elements.

        :rtype: bool
        """
        pass

    @abstractmethod
    def largest(self):
        """Get the largest element in the set if it exists, ``None`` otherwise.

        :rtype: .Surreal
        """
        pass

    @abstractmethod
    def smallest(self):
        """Get the smallest element in the set if it exists, ``None`` otherwise.

        :rtype: .Surreal
        """
        pass

    def birthday(self):
        """Get the largest birthday of any member of the set.

        If the :meth:`.Surreal.birthday` method of any of the elements of the
        set returns ``None``, also returns ``None``. If the set is empty returns
        zero.
        """
        return None

    def birthday_finite(self):
        """If all elements have a finite birthday.

        Returns True if the set is empty.

        :rtype: bool
        """
        return False

    def inner_repr(self, maxlen=None):
        """Text representation as comma-joined list of item reprs.

        Uses :meth:`.Surreal.simple_repr` for items.

        :param int maxlen: Maximum number of items to include. If None will use
            a default number.
        :rtype: str
        """
        return '???'

    def __repr__(self):
        return '{{{}}}'.format(self.inner_repr())

    def __neg__(self): raise TransfiniteError()
    def __lt__(self, value): raise TransfiniteError()
    def __gt__(self, value): raise TransfiniteError()
    def __le__(self, value): raise TransfiniteError()
    def __ge__(self, value): raise TransfiniteError()
    def __add__(self, value): raise TransfiniteError()
    def __radd__(self, value): raise TransfiniteError()
    def __sub__(self, value): raise TransfiniteError()
    def __rsub__(self, value): raise TransfiniteError()


class FiniteSurrealSet(SurrealSet, Set):
    """ABC for a finite set of surreals."""

    def is_finite(self):
        return True

    def smallest(self):
        raise min(self) if self else None

    def largest(self):
        raise max(self) if self else None

    def birthday(self):
        if not hasattr(self, '_birthday'):
            self._birthday = 0
            self._birthday_finite = True

            for item in self:
                self._birthday_finite &= item.birthday_finite()

                bday = item.birthday()
                if bday is None:
                    self._birthday = None
                    break

                else:
                    self._birthday = max(self._birthday, bday)

        return self._birthday

    def birthday_finite(self):
        if not hasattr(self, '_birthday_finite'):
            self.birthday()

        return self._birthday_finite

    def inner_repr(self, maxlen=4):

        item_reprs = [
            item.simple_repr() for item in
            islice(self, maxlen if len(self) <= maxlen else maxlen - 1)
        ]

        if len(self) > maxlen:
            item_reprs.append('...')

        return ', '.join(item_reprs)

    def __neg__(self): return ExplicitSurrealSet(-i for i in self)

    def __le__(self, value): return all(i <= value for i in self)
    def __ge__(self, value): return all(i >= value for i in self)
    def __lt__(self, value): return all(i < value for i in self)
    def __gt__(self, value): return all(i > value for i in self)

    def __add__(self, value): return ExplicitSurrealSet(i + value for i in self)
    def __radd__(self, value): return ExplicitSurrealSet(value + i for i in self)
    def __sub__(self, value): return ExplicitSurrealSet(i - value for i in self)
    def __rsub__(self, value): return ExplicitSurrealSet(value - i for i in self)


class EmptySurrealSet(FiniteSurrealSet):
    """The empty set, as an instance of :class:`SurrealSet`.

    Used in canonical forms of several types of surreals.
    """

    def __contains__(self, item):
        return False

    def __len__(self):
        return 0

    def __iter__(self):
        return iter(())


class ExplicitSurrealSet(FiniteSurrealSet):
    """A surreal set which explicitly stores its contents.

    :param items: Collection of :class:`.Surreal`\\ s.
    """

    def __init__(self, items):
        try:
            self._items = list(map(Surreal.convert, items))
        except TypeError:
            if isinstance(items, numbers.Number):
                self._items = [Surreal.convert(items)]
            else:
                raise

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(self._items)

    def __contains__(self, item):
        return item in self._items


class BasicSurreal(Surreal):
    """A surreal number form constructed from arbitrary left/right sets.

    :param left: :class:`.SurrealSet` or python collection of :class:`.Surreal`
        of items in the left set.
    :param right: :class:`.SurrealSet` or python collection of :class:`.Surreal`
        of items in the right set.
    """

    def __init__(self, left, right):
        if isinstance(left, SurrealSet):
            self._left = left
        else:
            self._left = ExplicitSurrealSet(left)

        if isinstance(right, SurrealSet):
            self._right = right
        else:
            self._right = ExplicitSurrealSet(right)

    @property
    def left(self):
        return self._left

    @property
    def right(self):
        return self._right

    def birthday(self):
        raise NotImplementedError()

    def birthday_finite(self):
        raise NotImplementedError()

    def is_finite(self):
        raise NotImplementedError()

    def is_infinite(self):
        raise NotImplementedError()

    def is_infinitesimal(self):
        raise NotImplementedError()

    def is_real(self):
        raise NotImplementedError()

    def is_rational(self):
        raise NotImplementedError()

    def is_dyadic(self):
        raise NotImplementedError()

    def is_integral(self):
        raise NotImplementedError()

    def simple_repr(self):
        return self.full_repr()
