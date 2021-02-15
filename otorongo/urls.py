"""otorongo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.urls import path
from django.conf.urls.static import static

from votes.views import index, ingresos_2021, bienes_2021, candidato_2021,\
    search, sentencias_2021, partidos_sentencias_2021, sentencias_2021_json,\
    ingresos_2021_json, bienes_2021_json, partidos_sentencias_2021_json, robots_txt

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index),
    path('search/', search),
    path('2021/ingresos/', ingresos_2021),
    path('2021/json/ingresos/', ingresos_2021_json),
    path('2021/bienes/', bienes_2021),
    path('2021/json/bienes/', bienes_2021_json),
    path('2021/sentencias/', sentencias_2021),
    path('2021/json/sentencias', sentencias_2021_json),
    path('2021/sentencias/<str:org_id>/', sentencias_2021),
    path('2021/partidos/sentencias/', partidos_sentencias_2021),
    path('2021/json/partidos/sentencias/', partidos_sentencias_2021_json),
    path('2021/candidato/<str:dni>/', candidato_2021),
    path('robots.txt',robots_txt),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
