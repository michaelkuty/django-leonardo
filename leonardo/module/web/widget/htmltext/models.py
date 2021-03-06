# -#- coding: utf-8 -#-

from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _
from leonardo.module.web.models import Widget


class HtmlTextWidget(Widget):
    '''Simple HTML Widget'''

    icon = "fa fa-file-text-o"

    text = models.TextField(
        _('text'), blank=True, default="<p>%s</p>" % ('Empty element'))

    widgets = {
        'text': forms.Textarea()
    }
    form_size = 'lg'

    class Meta:
        abstract = True
        verbose_name = _('HTML text')
        verbose_name_plural = _('HTML texts')

    def save(self, *args, **kwargs):
        if self.text == '':
            self.text = "<p>%s</p>" % _('Empty element')
        super(HtmlTextWidget, self).save(*args, **kwargs)
