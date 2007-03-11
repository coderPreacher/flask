# -*- coding: utf-8 -*-
"""
    jinja.exceptions
    ~~~~~~~~~~~~~~~~

    Jinja exceptions.

    :copyright: 2007 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""


class TemplateError(RuntimeError):
    pass


class SecurityException(TemplateError):
    """
    Raise if the template designer tried to do something dangerous.
    """


class FilterNotFound(KeyError, TemplateError):
    """
    Raised if a filter does not exist.
    """

    def __init__(self, message):
        KeyError.__init__(self, message)


class TestNotFound(KeyError, TemplateError):
    """
    Raised if a test does not exist.
    """

    def __init__(self, message):
        KeyError.__init__(self, message)


class TemplateNotFound(IOError, TemplateError):
    """
    Raised if a template does not exist.
    """

    def __init__(self, message):
        IOError.__init__(self, message)


class TemplateSyntaxError(SyntaxError, TemplateError):
    """
    Raised to tell the user that there is a problem with the template.
    """

    def __init__(self, message, lineno):
        SyntaxError.__init__(self, message)
        self.lineno = lineno


class TemplateRuntimeError(TemplateError):
    """
    Raised by the template engine if a tag encountered an error when
    rendering.
    """
