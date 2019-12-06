from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path, re_path

from .services.views import (
    CreateCredentialsView,
    ResetView,
    SetAuthorizationsView,
    ViewAuthView,
)

handler500 = "token_issuer.utils.views.server_error"
admin.site.site_header = "token_issuer admin"
admin.site.site_title = "token_issuer admin"
admin.site.index_title = "Welcome to the token_issuer admin"

urlpatterns = [
    # url(r'^admin_tools/', include('admin_tools.urls')),
    path(
        "admin/password_reset/",
        auth_views.PasswordResetView.as_view(),
        name="admin_password_reset",
    ),
    path(
        "admin/password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path("admin/", admin.site.urls),
    re_path(
        r"^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    # Simply show the master template.
    path("", CreateCredentialsView.as_view(), name="index"),
    path("view-auth/", ViewAuthView.as_view(), name="view-auth"),
    path("set-auth/", SetAuthorizationsView.as_view(), name="set-auth"),
    path("reset/", ResetView.as_view(), name="reset"),
]

# NOTE: The staticfiles_urlpatterns also discovers static files (ie. no need to run collectstatic). Both the static
# folder and the media folder are only served via Django if DEBUG = True.
urlpatterns += staticfiles_urlpatterns() + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)

if settings.DEBUG and "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
