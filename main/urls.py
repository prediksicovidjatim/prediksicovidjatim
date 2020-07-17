from django.urls import path, include

from django.contrib import admin

admin.autodiscover()

import web.views

# To add a new path, first import the app:
# import blog
#
# Then add the new path:
# path('blog/', blog.urls, name="blog")
#
# Learn more here: https://docs.djangoproject.com/en/2.1/topics/http/urls/

urlpatterns = [
    path("", web.views.index, name="index"),
    path("db/", web.views.db, name="db"),
    path("admin/", admin.site.urls),
    path("notebook/<path:nb_path>", web.views.notebook),
    path("grafik/", web.views.kabko),
    path("grafik/<str:kabko>", web.views.grafik),
]
