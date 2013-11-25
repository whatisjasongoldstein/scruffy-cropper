from django.conf.urls import patterns, url, include
from .views import CropView

urlpatterns = patterns('',
    url(r'^(?P<app>[-\w\d]+)/(?P<model>[-\w\d]+)/(?P<obj_id>[1-9]\d*)/(?P<field>[-\w\d]+)/$', CropView.as_view(), name="crop"),
)