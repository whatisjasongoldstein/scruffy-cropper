from django import forms
from django.contrib.contenttypes.models import ContentType
from cropper.models import Crop

ROTATE_OPTIONS = (
    (0, ''),
    (90, '90 degrees clockwise'),
    (270, '90 degrees counter-clockwise'),
    (180, '180 degrees'),
)


class CropImageForm(forms.Form):
    """ A form for cropping images on the account. """

    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop('model', None)
        self.field = kwargs.pop('field')
        self.coordinates = kwargs.pop('coordinates')
        self.image = getattr(self.model, self.field)

        super(CropImageForm,self).__init__(*args,**kwargs)
        self.fields['crop'].initial = self.coordinates or ""
        self.fields['crop'].widget = forms.HiddenInput()

    crop = forms.CharField()
    # rotate = forms.ChoiceField(required=False, choices=ROTATE_OPTIONS) # Maybe implement later
    
    required_css_class = 'required'

    def _parse_crop_coords(self, coords):
        
        if not coords:
            return None

        parts = coords.split(',')

        if len(parts) is not 4:
            raise ValueError('Invalid number of coordinates: {0}. Should be 4'.format(len(parts)))

        # Explode of these aren't integers
        parts = [int(part) for part in parts]

        # Make tuple of tuple and return
        return parts

    def clean(self):
        cleaned_data = super(CropImageForm, self).clean()

        # Clean crop field or fail
        try:
            cleaned_data['crop'] = self._parse_crop_coords(self.cleaned_data.get('crop'))
        except Exception:
            self._errors['crop'] = self.error_class(
                ["Um... somehow you messed with the crop data. I have no sympathy. Get out."])
            if 'crop' in cleaned_data:
                cleaned_data.pop('crop')

        # Asign it to the class if it's still here
        self.coordinates = self.data.get('crop')
        return cleaned_data


    def save(self):
        """ This is what saves the cropped version. """
        if self.coordinates:
            crop = Crop.objects.get_or_create(object_id=self.model.id, 
                content_type=ContentType.objects.get_for_model(self.model), field=self.field)[0]
            crop.coordinates = self.coordinates
            crop.save()
            crop.generate()
            return crop
        return False

