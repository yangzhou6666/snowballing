from .operations import reload

APPROACHES = []

class Group:
    """ Represents an Approach or a Group of work 

    The positional arguments in a group represents its works
    The keyword arguments sets attributes for the group and its works
      The exception is the dont_cite keyword argument, which also describes
      a list of work

    Expected attributes:
      _cite: indicates if wheter the approach has a display name or not
        True indicates that the approach must be referenced by its authors
        False indicates that the approach can referenced by name 
      _meta: list of dicts with attributes for comparing approaches
        A single approach can have more than one meta dict
        It is possible to use the distinct meta dicts to describe different aspects
      _about: HTML describing the approach

    Doctest:
    >>> from .operations import reload, work_by_varname
    >>> reload()
    >>> murta2014a = work_by_varname("murta2014a")
    >>> pimentel2015a = work_by_varname("pimentel2015a")
    >>> pimentel2015a.display == "now"
    False
    >>> APPROACHES.clear()
    >>> len(APPROACHES)
    0
    >>> group = Group(
    ...     murta2014a, pimentel2015a,
    ...     display="now",
    ...     _cite=True,
    ...     _meta=[dict(
    ...       scripts=True
    ...     )]
    ... )
    >>> group.display
    'now'
    >>> pimentel2015a.display == "now"
    True
    >>> len(APPROACHES)
    1
    """
    _category = "Related"
    def __init__(self, *args ,**kwargs):
        self.work = list(args)
        if 'dont_cite' in kwargs:
            self.work += kwargs['dont_cite']
            self.dont_cite = kwargs['dont_cite']
            del kwargs['dont_cite']

        for key, item in kwargs.items():
            for arg in self.work:
                if not hasattr(arg, 'force_' + key):
                    setattr(arg, key, item)
            setattr(self, key, item)

        if self._category == "Related":
            APPROACHES.append(self)

class GroupUnrelated(Group):
    """ Represents an Unrelated group of approaches 
    It does not add the approach into the APPROACHES list
    
    Doctest:
    >>> from .operations import reload, work_by_varname
    >>> reload()
    >>> murta2014a = work_by_varname("murta2014a")
    >>> pimentel2015a = work_by_varname("pimentel2015a")
    >>> pimentel2015a.display == "now"
    False
    >>> APPROACHES.clear()
    >>> len(APPROACHES)
    0
    >>> group = GroupUnrelated(
    ...     murta2014a, pimentel2015a,
    ...     display="now"
    ... )
    >>> group.display
    'now'
    >>> pimentel2015a.display == "now"
    True
    >>> len(APPROACHES)
    0
    """
    _category = "Unrelated"



def name(approach):
    """ Returns approach name. Removes double spaces in display 

    Doctest
    >>> from snowballing.operations import reload
    >>> reload()
    >>> [[a, m]] = get_approaches()
    >>> name(a)
    'noWorkflow'
    """
    return approach.display.replace("  ", "")


def wcite(approach, works, extra=""):
    """ Returns a latex cite command with all work in an approach """
    return ' \\cite{}{{{}}}'.format(
        extra,
        ', '.join([
            works[w]['ID'] 
            for w in approach.work
            if w in works
            if "snowball" in w.category
        ])
    )


def wlatex_name(approach, works):
    """ Returns approach name or latex citation according to attribute _cite """
    if not approach._cite:
        return name(approach)
    return wcite(approach, works, "t")


def wcitea(approach, works):
    """ Returns approach name followed by latex citation """
    if not approach._cite:
        return name(approach) + wcite(approach, works)
    return wcite(approach, works, "t")


def get_approaches(condition=None):
    """ Returns pairs of approaches and meta dicts 

    Doctest
    >>> from snowballing.operations import reload
    >>> reload()
    >>> len(get_approaches())
    1
    """
    if not condition:
        condition = lambda approach, meta: True
    reload()

    all_approaches = [
        (approach, meta)
        for approach in APPROACHES
        for meta in approach._meta
        if condition(approach, meta)
    ]

    return all_approaches
    

class Item:
    """ Constant Item that support additional descriptions """
    def __init__(self, value, _star=None, _bool=True, _examples=[]):
        self.value = value
        self._star = _star
        self._bool = _bool
        self._examples = _examples

    def star(self, text):
        return Item(self.value, _star=text, _bool=self._bool, _examples=self._examples)

    def such_as(self, examples):
        return Item(self.value, _star=self._star, _bool=self._bool, _examples=examples)

    def __eq__(self, other):
        if isinstance(other, Item):
            return self.value == other.value
        return self.value == other

    def __hash__(self):
        return hash(self.value)

    def __bool__(self):
        return self._bool

    @property
    def text(self):
        if self._star is None:
            return str(self.value)
        return str(self._star)
    
    def __repr__(self):
        if self._examples:
            return "{} ({})".format(self.text, ', '.join(map(str, self._examples)))
        return self.text

    def __str__(self):
        return repr(self)
