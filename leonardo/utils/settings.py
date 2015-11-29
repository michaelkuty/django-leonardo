

from importlib import import_module
from django.utils import six
from .versions import get_versions

import warnings


class dotdict(dict):

    """ Dictionary with dot access """

    def __getattr__(self, attr):
        return self.get(attr, None)
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class Config(dict):

    """Simple Module Config Object
    encapsulation of dot access dictionary

    use dictionary as constructor

    """

    def get_value(self, key, values):
        '''Accept key of propery and actual values'''
        return merge(values, self.get_property(key))

    def get_property(self, key):
        """Expect Django Conf property"""
        _key = DJANGO_CONF[key]
        return getattr(self, _key, CONF_SPEC[_key])

    @property
    def module_name(self):
        """Module name from module if is set"""
        if hasattr(self, "module"):
            return self.module.__name__
        return None

    @property
    def name(self):
        """Distribution name from module if is set"""
        if hasattr(self, "module"):
            return self.module.__name__.replace('_', '-')
        return None

    @property
    def version(self):
        """return module version"""
        return get_versions([self.module_name]).get(self.module_name, None)

    @property
    def latest_version(self):
        """return latest version if is available"""
        from leonardo_system.pip import check_versions
        return check_versions(True).get(self.name, None).get('new', None)

    @property
    def needs_migrations(self):
        """Indicates whater module needs migrations"""
        # TODO(majklk): also check models etc.
        if len(self.widgets) > 0:
            return True
        return False

    @property
    def needs_sync(self):
        """Indicates whater module needs templates, static etc."""

        affected_attributes = [
            'css_files', 'js_files',
            'scss_files', 'widgets']

        for attr in affected_attributes:
            if len(getattr(self, attr)) > 0:
                return True
        return False

    def set_module(self, module):
        """Just setter for module"""
        setattr(self, "module", module)

    def __getattr__(self, attr):
        return self.get(attr, None)

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


CONFIG_VALID = (list, tuple, dict)


def merge(a, b):
    """return merged tuples or lists without duplicates
    note: ensure if admin theme is before admin
    """
    if isinstance(a, CONFIG_VALID) \
            and isinstance(b, CONFIG_VALID):
        # dict update
        if isinstance(a, dict) and isinstance(b, dict):
            a.update(b)
            return a
        # list update
        _a = list(a)
        for x in list(b):
            if x not in _a:
                _a.append(x)
        return _a
    if a and b:
        raise Exception("Cannot merge")
    raise NotImplementedError