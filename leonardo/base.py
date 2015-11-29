
import warnings

from app_loader.base import AppLoader
from django.conf.urls import include, patterns, url
from django.utils import six
from django.utils.functional import cached_property
from django.utils.module_loading import module_has_submodule  # noqa
from importlib import import_module  # noqa
from leonardo.conf import Default
from leonardo.decorators import _decorate_urlconf, require_auth
from leonardo.utils.settings import merge


# use leonardo instead
default = Default()


class Leonardo(AppLoader):

    default = default

    CONFIG_MODULE_PREFIX = "LEONARDO"
    CONFIG_MODULE_SPEC_CLASS = "leonardo.conf.spec.CONF_SPEC"
    CONFIG_MODULE_OBJECT_CLASS = "leonardo.utils.settings.Config"

    @cached_property
    def urlpatterns(self):
        '''load and decorate urls from all modules
        then store it as cached property for less loading
        '''
        urlpatterns = []
        # load all urls
        # support .urls file and urls_conf = 'elephantblog.urls' on default module
        # decorate all url patterns if is not explicitly excluded
        for mod in leonardo.modules:
            # TODO this not work
            if self.is_leonardo_module(mod):

                conf = self.get_conf_from_module(mod)

                if module_has_submodule(mod, 'urls'):
                    urls_mod = import_module('.urls', mod.__name__)
                    if hasattr(urls_mod, 'urlpatterns'):
                        # if not public decorate all

                        if conf['public']:
                            urlpatterns += urls_mod.urlpatterns
                        else:
                            _decorate_urlconf(urls_mod.urlpatterns,
                                              require_auth)
                            urlpatterns += urls_mod.urlpatterns
        # avoid circural dependency
        # TODO use our loaded modules instead this property
        from django.conf import settings
        for urls_conf, conf in six.iteritems(getattr(settings, 'MODULE_URLS', {})):
            # is public ?
            try:
                if conf['is_public']:
                    urlpatterns += \
                        patterns('',
                                 url(r'', include(urls_conf)),
                                 )
                else:
                    _decorate_urlconf(
                        url(r'', include(urls_conf)),
                        require_auth)
                    urlpatterns += patterns('',
                                            url(r'', include(urls_conf)))
            except Exception as e:
                raise Exception('raised %s during loading %s' % (str(e), urls_conf))
        return urlpatterns


leonardo = Leonardo()
