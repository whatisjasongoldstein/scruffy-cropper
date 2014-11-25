Scruffy Cropper for Django
==========================

**Rewritten to take advantage of Class Based Views. Seems to work. Updated docs and tests to come.**


A reusable part to let users crop their uploaded images.

## Usage

Let's say you have something like this:

    class Foo(models.Model):
        photo = models.ImageField(...)

And you want users to be able to crop this photo without destroying the original.

### Setting up

pip install this from git and add 'cropper' to settings.INSTALLED_APPS.

Make a template that handles the javascript and form side. I have an example that will work in the admin, but I assume you're particular about UI... right?

The main view is `cropper.views.CropView` as is designed to be subclassed, but for starters, adding `url(r'^crop/', include('cropper.urls'))` should work just fine.

### Helpers

I've included some helper methods to help keep GFK dirt out of your code. They are...

    from cropper.helpers import get_or_create_crop, get_cropped_image, delete_crop

They all take a model instance and a field name (as a string).


### Meanwhile, back at the models.py

Your model should subclass CroppableImageMixin. It overrides save to wipe out any obsolete crops if you update one of your croppable images.

Now we're in a state where we may or may not have a cropped image... so let's add a property of the model to handle that.

    from cropper.models import CroppableImageMixin
    from cropper.helpers import get_cropped_image

    class Foo(CroppableImageMixin):
        photo = models.ImageField(...)

        @property
        def cropped_photo(self):
            """ Return the photo, look for a cropped version first. """
            crop = get_cropped_image(self, 'photo')  # Returns None if there's no cropped version.
            return crop or self.photo

And then in the template - or anywhere else for that matter - foo.cropped_photo will always return what you want.

Using the CropWidget on forms is still hairy. I wind up doing something like:

```python
from django import forms
from django.core.urlresolvers import reverse
from cropper.widgets import CropImageWidget

class FooForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(PostForm,self).__init__(*args,**kwargs)

        obj = kwargs.get('instance')

        # If there's an instance, we can crop. Otherwise that field is sort of irrelevant.
        crop_attrs={}
        if obj and obj.id:
            self.cropper_url = reverse('crop',kwargs=dict(
                app=self._meta.model._meta.app_label, 
                model=self._meta.model._meta.model_name, 
                obj_id=obj.id, 
                field='image',))
            crop_attrs = {
                'data-crop-url': self.cropper_url, 
                'post-save-redirect': self.redirect_url,  # pass it in kwargs, this is where you go faster you save
            }

        self.fields['photo'] = forms.ImageField(widget=CropImageWidget(attrs=crop_attrs), required=False)
        
    class Meta:
        model = Foo
```

This is pretty terrible and could benefit from a little more magic under the hood.

### Other requirements

It also assumes you use [easy-thumbnails](https://github.com/SmileyChris/easy-thumbnails). But anything (solr-thumbnails) that uses the same API should work fine.


### Other Notes

* Always use get_or_create when dealing with crops. There should only be one on a field.
* Pillow is required. I don't list it as a dependency because installing it on almost any OS is hairy, and if you haven't done it yet, the usual pip install probably won't help you anyway.
* On the front end, I have a submit button with the name 'delete', and another with 'save'. The view ignores there values, it just cares if 'delete' is in POST, so you can change the user-facing text at your discretion.
* Anything jcrop supports should work. There's a little bit of js at the bottom of the template that translates between PIL-acceptable coordinates and jcrop coordinates.
* The jcrop can't be applied to the image until ready state because the image being cropped has to be fully loaded, or the initial crop area winds up as 0x0.
* Responsive? Touch support? Absolutely.

