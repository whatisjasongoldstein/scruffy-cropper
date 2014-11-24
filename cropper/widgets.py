from django.forms import ClearableFileInput, CheckboxInput
from django.template.defaultfilters import urlencode
from django.template.loader import render_to_string



class CropImageWidget(ClearableFileInput):
    """ ClearableFileInput with thumbnails and crop. """

    class Media:
        css = {
            "all": ("cropper/widgets.css",),
        }

    def render(self, name, value, attrs=None):

        link = None
        if value and hasattr(value, "url"):
            link = value.url

        checkbox_name = self.clear_checkbox_name(name)
        checkbox_id = self.clear_checkbox_id(checkbox_name)
        context = {
            'initial_text': self.initial_text,
            'input_text': self.input_text,
            'clear_template': '',
            'clear_checkbox_label': self.clear_checkbox_label,
            'required': self.is_required,
            'input': super(ClearableFileInput, self).render(name, value, attrs),
            'value': value,
            'link': link,
            'attrs': attrs,
            'crop_url': self.attrs.get('data-crop-url'),
            'crop_redirect': urlencode(self.attrs.get('post-save-redirect') or ""),
            'clear': CheckboxInput().render(checkbox_name, False, attrs={'id': checkbox_id}),
            'required': self.is_required,
        }

        return render_to_string('cropper/crop_widget.html', context)


