from django.contrib.contenttypes.models import ContentType
from .models import Crop


def get_or_create_crop(obj, field_name):
    """ Makes the crop. """
    crop = Crop.objects.get_or_create(object_id = obj.id, 
            content_type = ContentType.objects.get_for_model(obj),
            field = field_name,
        )[0]
    return crop


def get_cropped_image(obj, field_name):
    """ Returns a cropped image or None. """
    crop = Crop.objects.filter(object_id = obj.id, 
            content_type = ContentType.objects.get_for_model(obj),
            field = field_name,
        )
    if crop:
        return crop[0].image
    return None


def delete_crop(obj, field_name):    
    crop = Crop.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(obj), field=field_name)
    if not crop:
        return False

    crop.delete()
    return True