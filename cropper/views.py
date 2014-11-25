import json
from django.http import Http404, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models.loading import get_model
from django.views.generic import View
from django.utils.functional import cached_property

from easy_thumbnails.files import get_thumbnailer

from .forms import CropImageForm
from .helpers import get_or_create_crop, delete_crop


class CropBase(View):

    @cached_property
    def model(self):
        model = get_model(self.kwargs['app'], self.kwargs['model'])
        if not model:
            raise Http404()
        return model

    @cached_property
    def obj(self):
        self.field = self.kwargs['field']
        return get_object_or_404(self.model, id=self.kwargs['obj_id'])

    @cached_property
    def image(self):
        thr = get_thumbnailer(getattr(self.obj, self.field))
        return thr.get_thumbnail({"size": (800, 600)}).url

    @cached_property
    def params(self):
        return self.request.GET or self.request.POST

    @cached_property
    def post_save_redirect(self):
        return self.params.get('post-save-redirect', '/')

    @cached_property
    def crop(self):
        return get_or_create_crop(self.obj, self.field)

    @cached_property
    def coordinates(self):
        return self.crop.coordinates

    @cached_property
    def form(self):
        return CropImageForm(self.request.POST or None, 
            coordinates=self.coordinates, 
            model=self.obj, field=self.kwargs['field'])

    @cached_property
    def context(self):
        return {
            'form': self.form,
            'coordinates': self.coordinates,
            'post_save_redirect': self.post_save_redirect,
            'image': self.image,
        }


class CropView(CropBase):
    """Regular page-crop view."""
    base_template = "admin/base_site.html"
    template_name = "cropper/crop.html"

    def get(self, request, **kwargs):
        return render(request, self.template_name, self.context)

    def post(self, request, **kwargs):

        # So we can reuse this view, passing 'delete' in POST will kill it and abort
        if 'delete' in request.POST:
            delete_crop(self.obj, self.field)
            messages.add_message(request, messages.SUCCESS, 'No crop? No problem..')
            return redirect(self.post_save_redirect)

        if self.form.is_valid():
            self.form.save()
            messages.add_message(request, messages.SUCCESS, 'Crop saved! That was easy.')
            return redirect(self.post_save_redirect)

        messages.add_message(request, messages.ERROR, "Not a valid crop.")
        return self.get(request, **kwargs)

    @cached_property
    def context(self):
        context = super(CropView, self).context
        context.update({
            "base_template": self.base_template,
        })
        return context


class CropAnywhereView(CropBase):
    """For ajax. Works with crop-anywhere.js"""

    message = None
    success = True

    def render_response(self):
        data = {
            "image": self.image,
            "message": self.message,
            "status": self.success,
            "url": self.request.path,
            "coordinates": self.coordinates,
            "dimensions": self.crop.dimensions,
        }
        return HttpResponse(json.dumps(data), content_type="application/json")

    def get(self, *args, **kwargs):
        return self.render_response()

    def post(self, request, *args, **kwargs):
        if 'delete' in request.POST:
            delete_crop(self.obj, self.field)
            self.message = "No crop? No problem.."
            return self.render_response()

        if self.form.is_valid():
            self.form.save()
            self.message = "Crop saved! That was easy."
            return self.render_response()

        self.message = "Not a valid crop."
        return self.render_response()

