"""Citibutler Web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/stable/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.views.generic import RedirectView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from apps.teams.urls import team_urlpatterns as single_team_urls
from apps.subscriptions.urls import team_urlpatterns as subscriptions_team_urls

from .auth import Auth0Login

# urls that are unique to using a team should go here
team_urlpatterns = [
    path("subscription/", include(subscriptions_team_urls)),
    path("team/", include(single_team_urls)),
]

urlpatterns = [
    path("", RedirectView.as_view(url="/admin"), name='home'),
    path("ctibutler_api/", include("ctibutler_api.urls")),
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    # redirect Django admin login to main login page
    path("admin/login/", RedirectView.as_view(pattern_name="auth0_login")),
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("users/", include("apps.users.urls")),
    path("team-management/<str:team_id>/", include(team_urlpatterns)),
    path("subscriptions/", include("apps.subscriptions.urls")),
    path("teams/", include("apps.teams.urls")),
    # path("celery-progress/", include("celery_progress.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path("stripe/", include("djstripe.urls", namespace="djstripe")),
    path("rest-auth/auth0/", Auth0Login.as_view(), name="auth0_api_login"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.ENABLE_DEBUG_TOOLBAR:
    urlpatterns.append(path("__debug__/", include("debug_toolbar.urls")))
