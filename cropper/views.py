from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib import messages
from django.db.models.loading import get_model

from cropper.models import Crop
from cropper.forms import CropImageForm


def delete_crop(request, app, model_name, obj_id, field, redirect_to="/"):
    """ Delete a crop. """
    
    # Get the crop for this field on this object.
    model = get_object_or_404(ContentType, app_label=app, name=model_name)
    crop = get_object_or_404(Crop, content_type=model, object_id=obj_id, field=field)

    crop.delete()

    return redirect(redirect_to)



def create_crop(request, app, model_name, object_id, field, template='cropper/crop.html'):
    """ Create a crop, or edit an existing one. This is an example of a wrapping view.

    Notice there is no security around this view. I would not call it directly without a wrapper
    view or decorator that ensures it's okay for the user to access it.
    """

    # Get the object we want to work with
    model = get_model(app, model_name)
    obj = get_object_or_404(model, id=object_id)

    # get_object_or_404(Account, project_name=userslug)

    # Get any existing crop coordinates to pass along
    coordinates = Crop.objects.get_or_create(object_id = obj.id, 
            content_type = ContentType.objects.get_for_model(obj),
            field = field,
        )[0].coordinates

    form = CropImageForm(request.POST or None, coordinates=coordinates, model=obj, field=field)

    if request.POST:
        if form.is_valid():
            crop = form.save()
            coordinates = crop.coordinates
            messages.add_message(request, messages.SUCCESS, 'Crop saved! That was easy.')
        else:
            messages.add_message(request, messages.ERROR, "WTF? Something is wrong.")

    return render(request, template, {
            'form': form,
            'coordinates': coordinates,
        })
