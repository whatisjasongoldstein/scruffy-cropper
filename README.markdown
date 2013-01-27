Scruffy Cropper for Django
==========================

A reusable part to let users crop their uploaded images. On the front end, I'm using [jCrop](http://deepliquid.com/content/Jcrop.html) on the front end, PIL in back.

## Usage

Let's say you have something like this:

    class Foo(models.Model):
        photo = models.ImageField(...)

And you want users to be able to crop this photo without destroying the original.

### Setting up

pip install this from git and add 'cropper' to settings.INSTALLED_APPS.

Make a template that handles the javascript and form side. I have an example, but I assume you're particular about UI... right?

The main view is **cropper.views.create_crop**, and while you could point a URL at it, because there's no security checks or logic ensuring what kind of fields you want to crop, it'd be smart to wrap it in your own view.

    @login_required
    def crop(request):
        obj = Foo.objects.get(owner=request.user)
        next = reverse('foo.dashboard')

        # Other logic, maybe?

        # Args in order: request, app_label, model name, model instance id, field name, template, and the url to go post save or delete
        return create_crop(request, 'my_app_label', 'foo', obj.id, 'photo', 'my_crop_template.html', post_save_redirect=next)

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


### Other requirements

It also assumes you use easy-thumbnails. But anything (solr-thumbnails) that uses the same API should work fine.


### Other Notes

* Always use get_or_create when dealing with crops. There should only be one on a field.
* PIL is required. I don't list it as a dependency because installing PIL on almost any OS is hairy, and if you haven't done it yet, the usual pip install probably won't help you anyway.
* On the front end, I have a submit button with the name 'delete', and another with 'save'. The view ignores there values, it just cares if 'delete' is in POST, so you can change the user-facing text at your discretion.
* Anything jcrop supports should work. There's a little bit of js at the bottom of the template that translates between PIL-acceptable coordinates and jcrop coordinates.
* The jcrop can't be applied to the image until ready state because the image being cropped has to be fully loaded, or the initial crop area winds up as 0x0.
* Responsive? Touch support? Absolutely.

