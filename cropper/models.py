import PIL
import hashlib
from django.db import models
from django.utils.functional import cached_property
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class CroppableImageMixin(models.Model):
    """ Handles post save logic for models that have croppable image fields. """

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """ Delete any crops if an image changes. """
        from cropper.helpers import delete_crop
        if self.id: # only existing versions
            croppable_fields = [field for field in self._meta.fields if field.__class__.__name__ == "ImageField"]
            old = self.__class__.objects.get(id=self.id)  # Before this save
            for field in croppable_fields:
                if getattr(self, field.name) != getattr(old, field.name): # If the file is different
                    delete_crop(self, field.name)  # Wipe out whatever applies
        return super(CroppableImageMixin, self).save(*args, **kwargs)
        

class Crop(models.Model):
    """ A cropped version of an imagefield from another model. """
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    field = models.CharField(max_length=255, help_text="The imagefield's name")
    image = models.ImageField(upload_to="crop/")
    coordinates = models.TextField(default="")

    def generate(self):
        obj = self.content_object
        field = getattr(obj, self.field)
        image = ContentFile(field.file.read())

        # Get extension
        if "." in field.file.name:
            split_file_name = field.file.name.split('.')
            split_file_name.reverse()
            extension = split_file_name[0]
        else:
            extension = "jpg"

        # Make hash filename to ensure uniqueness
        filename_hash = hashlib.md5(field.file.name)
        filename_hash = filename_hash.hexdigest()

        # Build filename
        image.name = "{model}.{obj}.{field}.{filename}.{ext}".format(
            model=obj._meta.db_table, obj=self.object_id, field=self.field, 
            ext=extension, filename=filename_hash)

        # Save to model
        self.image = image
        self.save()

        # if self.coordinates:
        self._crop_image()


    @cached_property
    def dimensions(self):
        """
        Looking this up requires opening the image in PIL.
        Cache it forever.
        """
        img_field = getattr(self.content_object, self.field)
        key = "scruffycropper.dimensions.{}".format(hashlib.md5(self.image.name).hexdigest())
        dimensions = cache.get(key)
        if not dimensions:
            dimensions = [img_field.width, img_field.height]
            cache.set(key, dimensions)
        return dimensions

    def _crop_image(self):
        """ Does the PIL work. """
        im = PIL.Image.open(self.image.file.name)
        coordinates = [int(point) for point in self.coordinates.split(',')]
        im = im.crop(coordinates)
        im.save(self.image.file.name)

