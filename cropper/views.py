from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models.loading import get_model
from django.views.generic import View
from django.utils.functional import cached_property
from .forms import CropImageForm
from .helpers import get_or_create_crop, delete_crop


class CropView(View):
    base_template = "admin/base_site.html"
    template_name = "cropper/crop.html"
    post_save_redirect = "/"
    

    def dispatch(self, request, *args, **kwargs):

        self.app = self.kwargs['app']
        self.model_name = self.kwargs['model']
        self.field = self.kwargs['field']
        self.coordinates = None

        self.model = get_model(self.app, self.model_name)
        if not self.model: # No clue what this model is.
            raise Http404()

        self.obj = get_object_or_404(self.model, id=self.kwargs['obj_id'])

        # Could be in either GET or POST. Don't do this at home.
        generic_params = request.GET or request.POST
        self.post_save_redirect = generic_params.get('post-save-redirect') or self.post_save_redirect

        return super(CropView, self).dispatch(request, *args, **kwargs)


    def get_form(self, data):
        if hasattr(self, '_form'):
            return self._form
        self.coordinates = get_or_create_crop(self.obj, self.field).coordinates
        self._form = CropImageForm(data, coordinates=self.coordinates, model=self.obj, field=self.field)
        return self._form

    def get(self, request, **kwargs):
        form = self.get_form(None)
        return render(request, self.template_name, {
                'form': form,
                'coordinates': self.coordinates,
                'post_save_redirect': self.post_save_redirect,
                'base_template': self.base_template,
            })

    def post(self, request, **kwargs):

        # So we can reuse this view, passing 'delete' in POST will kill it and abort
        if 'delete' in request.POST:
            delete_crop(self.obj, self.field)
            messages.add_message(request, messages.SUCCESS, 'No crop? No problem..')
            return redirect(self.post_save_redirect)

        form = self.get_form(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Crop saved! That was easy.')
            return redirect(self.post_save_redirect)

        messages.add_message(request, messages.ERROR, "Not a valid crop.")
        return self.get(request, **kwargs)
