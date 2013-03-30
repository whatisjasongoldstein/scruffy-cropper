from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models.loading import get_model
from cropper.forms import CropImageForm
from cropper.helpers import get_or_create_crop, delete_crop


def create_crop(request, app, model_name, object_id, field, template='cropper/crop.html', post_save_redirect="/"):
    """
    Create a crop, or edit an existing one. This is an example of a wrapping view.

    Notice there is no security around this view. I would not call it directly without a wrapper
    view or decorator that ensures it's okay for the user to access it.

    """

    # Get the object we want to work with
    model = get_model(app, model_name)
    obj = get_object_or_404(model, id=object_id)
    # So we can reuse this view, passing 'delete' in GET will kill it and abort
    if 'delete' in request.POST:
        delete_crop(obj, field)
        messages.add_message(request, messages.SUCCESS, 'No crop? No problem..')
        return redirect(post_save_redirect)

    # Get any existing crop coordinates to pass along
    coordinates = get_or_create_crop(obj, field).coordinates

    form = CropImageForm(request.POST or None, coordinates=coordinates, model=obj, field=field)

    if request.POST:
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Crop saved! That was easy.')
            return redirect(post_save_redirect)
        else:
            messages.add_message(request, messages.ERROR, "Not a valid crop.")

    return render(request, template, {
            'form': form,
            'coordinates': coordinates,
            'post_save_redirect': post_save_redirect,
        })
