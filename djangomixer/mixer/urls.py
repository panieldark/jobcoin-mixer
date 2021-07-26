

from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('mix/', mixer_form_page, name='mixer_form_page'),
	path('create_request/', create_request, name="create_request"),
	path('create_request_ajax/', create_request_ajax, name="create_request_ajax"),


	path('open_requests_api/', open_requests_api, name="open_requests_api")
]

app_name = 'mixer'
