# grocery_project/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Include the URLs from your 'store' app
    # The namespace 'store' is used here to match how you're using it in your templates (e.g., {% url 'store:home' %})
    # Your store/urls.py already defines app_name = 'store', which also enables namespacing.
    path('', include('store.urls', namespace='store')),
]
