Django Cropper
==============

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

### Meanwhile, back at the models.py

Now we're in a state where we may or may not have a cropped image... so let's add a property of the model to handle that.

    class Foo(models.Model):
        photo = models.ImageField(...)

        @property
        def cropped_photo(self):
        """ Return the photo, look for a cropped version first. """
        crops = Crop.objects.filter(content_type=ContentType.objects.get(app_label="my_app", model="foo"), 
            object_id=self.id, field='photo')
        if crops:
            return crops[0].image
        return self.photo

And then in the template - or anywhere else for that matter - foo.cropped_photo will always return what you want.

I also override save to ensure old crops are removed if the photo changes:

    def save(self, *args, **kwargs):
        """ Delete any crops if an image changes. """

        if self.id: # only existing versions
            croppable_fields = ['photo',]
            old = Foo.objects.get(id=self.id)  # Existing version of the object we're about to save
            for field in croppable_fields:
                if getattr(self, field).name != getattr(old, field).name: # If the file is different
                    Crop.objects.filter(
                        content_type=ContentType.objects.get(app_label="my_app", model="foo"), 
                        object_id=self.id, 
                        field=field
                    ).delete()  # Wipe out whatever applies

        return super(Foo, self).save(*args, **kwargs)

In the future some of this stuff might be inheritable... that'd be cool.

### The Shameful Widgets Module

Um... um... Okay, you've got me on this one. It's pretty gross. I'm really paricular about form styling - I want nice looking upload buttons, a 'currently' slot, clearing that I can actually put where I want it, thumbnails, and yes, now a crop button.

Django Forms are both awesome and royally suck when you try to extend them. Suggestions on sucking less are welcome.

It also assumes you use easy-thumbnails.


### Other Notes

* Always use get_or_create when dealing with crops. There should only be one on a field.
* PIL is required. I don't list it as a dependency because installing PIL on almost any OS is hairy, and if you haven't done it yet, the usual pip install probably won't help you anyway.
* On the front end, I have a submit button with the name 'delete', and another with 'save'. The view ignores there values, it just cares if 'delete' is in POST, so you can change the user-facing text at your discretion.
* Anything jcrop supports should work. There's a little bit of js at the bottom of the template that translates between PIL-acceptable coordinates and jcrop coordinates.
* The jcrop can't be applied to the image until ready state because the image being cropped has to be fully loaded, or the initial crop area winds up as 0x0.
* Responsive? Touch support? Absolutely.

