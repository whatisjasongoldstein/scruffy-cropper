import PIL
from django.db import models
from django.core.files.base import ContentFile
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

class Crop(models.Model):
    """ A cropped version of an imagefield from another model. """
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    field = models.CharField(max_length=255, help_text="The imagefield's name")
    image = models.ImageField(upload_to="crop/")
    coordinates = models.TextField(default="")

    def generate(self):
        obj = self.content_object
        field = getattr(obj, self.field)
        image = ContentFile(field.file.read())

        # Get extension
        split_file_name = field.file.name.split('.')
        split_file_name.reverse()
        extension = split_file_name[0]

        # Build filename
        image.name = "{model}.{obj}.{field}.{ext}".format(
            model=obj._meta.db_table, obj=self.object_id, field=self.field, ext=extension)

        # Save to model
        self.image = image
        self.save()

        # if self.coordinates:
        self._crop_image()


    def _crop_image(self):
        """ Does the PIL work. """
        im = PIL.Image.open(self.image.file.name)
        coordinates = [int(point) for point in self.coordinates.split(',')]
        im = im.crop(coordinates)
        im.save(self.image.file.name)
