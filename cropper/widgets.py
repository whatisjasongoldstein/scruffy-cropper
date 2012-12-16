from django.forms import ClearableFileInput, CheckboxInput
from django.utils.safestring import mark_safe
from django.template.defaultfilters import urlencode
from django.template import Template, Context

def _snippet(template="", context={}):
    """ Simple template render """
    t = Template(template)
    c = Context(context)
    html = t.render(c)
    return html


class CropImageWidget(ClearableFileInput):
    """ ClearableFileInput with thumbnails and crop. """

    def _crop_button(self, substitutions):
        link = self.attrs.get('data-crop-url')
        post_save_link = urlencode(self.attrs.get('post-save-redirect') or "")

        if not link:
            return ""
        return """<a class="button" href="%s?post-save-redirect=%s">Crop</a>""" % (link, post_save_link)

    def render(self, name, value, attrs=None):

        substitutions = {
            'initial_text': self.initial_text,
            'input_text': self.input_text,
            'clear_template': '',
            'clear_checkbox_label': self.clear_checkbox_label,
        }

        substitutions['input'] = super(ClearableFileInput, self).render(name, value, attrs)
        img = None
        if value and hasattr(value, "url"):
            substitutions['initial'] = '<a class="thumbTxt" href="%(link)s">%(txt)s</a>' % {
                'link':value.url, 'txt':value.name[:20] }

            img = _snippet(u'{% load thumbnail %}<img src="{% thumbnail photo "75x75" %}">', { 'photo': value })

            if not self.is_required:
                checkbox_name = self.clear_checkbox_name(name)
                checkbox_id = self.clear_checkbox_id(checkbox_name)
                substitutions['clear_checkbox_name'] = checkbox_name
                substitutions['clear_checkbox_id'] = checkbox_id
                substitutions['clear'] = CheckboxInput().render(checkbox_name, False, attrs={'id': checkbox_id})
                substitutions['clear_template'] = self.template_with_clear % substitutions

        styleable_input = '<b class="wrap_file_input">Select File %s</b><i class="current"></i>' % substitutions['input']
        
        clear_ui = "" # None by default
        if not self.is_required and substitutions.get('clear'):
            clear_ui = '<span>Clear %s</span>' % substitutions['clear']

        output_list = ['<span class="imgWidget">',]
        if substitutions.get('initial'):
            output_list += [
                '<b class="thumb">',
                    img,
                '</b>',
                '<i class="context">',
                        '<span>%s</span>' % substitutions['initial'],
                        '<span>Change {1} {0}</span>'.format(styleable_input, self._crop_button(substitutions)),
                        clear_ui,
                '</i>',
            ]
        else:
            output_list += [
                styleable_input,
            ]

        output_list += ['</span>',] # close wrapper
        output = u"".join(output_list)

        return mark_safe(output)

