from django.contrib import admin
from cropper.models import Crop

class CropAdmin(admin.ModelAdmin):
    list_display = ['content_object', 'content_type', 'object_id', 'field', 'image', 'coordinates',]
    list_filter = ['content_type', 'field']

admin.site.register(Crop, CropAdmin)
