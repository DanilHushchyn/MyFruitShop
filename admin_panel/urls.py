from django.urls import path

from admin_panel.views import *

urlpatterns = [
    path('', main, name='main'),
    path('upload-declaration', UploadDeclarationView.as_view(), name='declaration'),
]
