# -*- coding: utf-8 -*-
"""
    jinja.utils
    ~~~~~~~~~~~

    Utility functions.

    :copyright: 2007 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""
import re
from types import MethodType, FunctionType
from jinja.nodes import Trans
from jinja.datastructure import Markup

try:
    from collections import deque
except ImportError:
    deque = None


_escape_pairs = {
    '&':            '&amp;',
    '<':            '&lt;',
    '>':            '&gt;',
    '"':            '&quot;'
}

_escape_res = (
    re.compile('(&|<|>|")'),
    re.compile('(&|<|>)')
)


def escape(x, attribute=False):
    """
    Escape an object x.
    """
    return Markup(_escape_res[not attribute].sub(lambda m:
                  _escape_pairs[m.group()], x))


def find_translations(environment, source):
    """
    Find all translatable strings in a template and yield
    them as (lineno, singular, plural) tuples. If a plural
    section does not exist it will be None.
    """
    queue = [environment.parse(source)]
    while queue:
        node = queue.pop()
        if node.__class__ is Trans:
            yield node.lineno, node.singular, node.plural
        queue.extend(node.getChildNodes())


def buffereater(f):
    """
    Used by the python translator to capture output of substreams.
    (macros, filter sections etc)
    """
    def wrapped(*args, **kwargs):
        return u''.join(f(*args, **kwargs))
    return wrapped


class CacheDict(object):
    """
    A dict like object that stores a limited number of items and forgets
    about the least recently used items::

        >>> cache = CacheDict(3)
        >>> cache['A'] = 0
        >>> cache['B'] = 1
        >>> cache['C'] = 2
        >>> len(cache)
        3
    
    If we now access 'A' again it has a higher priority than B::

        >>> cache['A']
        0

    If we add a new item 'D' now 'B' will disappear::

        >>> cache['D'] = 3
        >>> len(cache)
        3
        >>> 'B' in cache
        False

    If you iterate over the object the most recently used item will be
    yielded First::

        >>> for item in cache:
        ...     print item
        D
        A
        C

    If you want to iterate the other way round use ``reverse(cache)``.

    Implementation note: This is not a nice way to solve that problem but
    for smaller capacities it's faster than a linked list.
    Perfect for template environments where you don't expect too many
    different keys.
    """

    def __init__(self, capacity):
        self.capacity = capacity
        self._mapping = {}

        # use a deque here if possible
        if deque is not None:
            self._queue = deque()
            self._popleft = self._queue.popleft
        # python2.3, just use a list
        else:
            self._queue = []
            pop = self._queue.pop
            self._popleft = lambda: pop(0)
        # alias all queue methods for faster lookup
        self._pop = self._queue.pop
        self._remove = self._queue.remove
        self._append = self._queue.append

    def copy(self):
        rv = CacheDict(self.capacity)
        rv._mapping.update(self._mapping)
        rv._queue = self._queue[:]
        return rv

    def get(self, key, default=None):
        if key in self:
            return self[key]
        return default

    def setdefault(self, key, default=None):
        if key in self:
            return self[key]
        self[key] = default
        return default

    def clear(self):
        self._mapping.clear()
        del self._queue[:]

    def __contains__(self, key):
        return key in self._mapping

    def __len__(self):
        return len(self._mapping)

    def __repr__(self):
        return '<%s %r>' % (
            self.__class__.__name__,
            self._mapping
        )

    def __getitem__(self, key):
        rv = self._mapping[key]
        if self._queue[-1] != key:
            self._remove(key)
            self._append(key)
        return rv

    def __setitem__(self, key, value):
        if key in self._mapping:
            self._remove(key)
        elif len(self._mapping) == self.capacity:
            del self._mapping[self._popleft()]
        self._append(key)
        self._mapping[key] = value

    def __delitem__(self, key):
        del self._mapping[key]
        self._remove(key)

    def __iter__(self):
        try:
            return reversed(self._queue)
        except NameError:
            return iter(self._queue[::-1])

    def __reversed__(self):
        return iter(self._queue)

    __copy__ = copy
