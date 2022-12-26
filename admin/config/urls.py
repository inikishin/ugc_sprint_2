from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(url="/admin")),
    path("admin/", admin.site.urls),
    path("__debug__/", include("debug_toolbar.urls")),
]
