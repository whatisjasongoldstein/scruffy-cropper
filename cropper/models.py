import PIL
from django.db import models
from django.core.files.base import ContentFile
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


# class CroppableImageMixin(models.Model):
#     """ 
#     EXPERTIMENTAL: DO NOT USE.

#     Handles post save logic for models that have croppable image fields.

#     """

#     class Meta:
#         abstract = True

#     def clear_old_crops(self, *args, **kwargs):
#         """ Delete any crops if an image changes. """
#         from cropper.helpers import delete_crop

#         if self.id: # only existing versions
#             fields = self._meta.fields
#             croppable_fields = [field for field in fields if field.__class__.__name__ == "ImageField"]

#             old = self.__class__.objects.get(id=self.id)  # Before this save
#             for field in croppable_fields:
#                 if getattr(self, field.name) != getattr(old, field.name): # If the file is different
#                     delete_crop(self, field)


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
