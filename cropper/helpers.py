from cropper.models import Crop
from django.contrib.contenttypes.models import ContentType

def get_or_create_crop(obj, field_name):
    # Get any existing crop coordinates to pass along
    crop = Crop.objects.get_or_create(object_id = obj.id, 
            content_type = ContentType.objects.get_for_model(obj),
            field = field_name,
        )[0]
    return crop

def delete_crop(obj, field_name):    
    crop = Crop.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(obj), field=field_name)
    if not crop:
        return False

    crop.delete()
    return True