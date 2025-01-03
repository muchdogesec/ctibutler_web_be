import requests
from django.shortcuts import render
from rest_framework.views import APIView
from apps.teams.permissions import TeamModelAccessPermissions
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.exceptions import (
    PermissionDenied,
)
from rest_framework.permissions import IsAdminUser
from .permisions import HasTeamApiKey


# Create your views here.
class CtiButlerProxyView(APIView):
    permission_classes = [HasTeamApiKey]

    def dispatch(self, request, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        request = self.initialize_request(request, *args, **kwargs)
        self.request = request
        self.headers = self.default_response_headers  # deprecate?

        try:
            self.initial(request, *args, **kwargs)
            if not HasTeamApiKey().has_permission(self.request, self):
                raise PermissionDenied()
            # Modify the target URL as needed
            target_url = (
                f"{settings.CTIBUTLER_SERVICE_BASE_URL}/api/v1/{kwargs['path']}"
            )
            if request.method != "GET":
                raise MethodNotAllowed()

            # Forward the request to the target URL
            headers = {
                key: value
                for key, value in request.headers.items()
                if (key != "Host" and key != "Content-Length")
            }
            response = requests.request(
                method="GET",
                url=target_url,
                headers=headers,
                data=request.body,
                params={key: value for key, value in request.GET.items()},
                allow_redirects=False,
            )

            # Return the response to the original request
            return HttpResponse(
                response.content,
                status=response.status_code,
                content_type=response.headers.get("Content-Type"),
            )
        except PermissionDenied:
            return HttpResponse(
                {},
                status=401,
            )
        except Exception as exc:
            response = self.handle_exception(exc)
            self.response = self.finalize_response(
                request, response, *args, **kwargs)
            return self.response

# Create your views here.
class AdminCtiButlerProxyView(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [SessionAuthentication, BasicAuthentication, TokenAuthentication]

    def dispatch(self, request, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        request = self.initialize_request(request, *args, **kwargs)
        self.request = request
        self.headers = self.default_response_headers  # deprecate?

        try:
            self.initial(request, *args, **kwargs)
            # Modify the target URL as needed
            target_url = (
                f"{settings.CTIBUTLER_SERVICE_BASE_URL}/api/v1/{kwargs['path']}"
            )

            # Forward the request to the target URL
            headers = {
                key: value
                for key, value in request.headers.items()
                if (key != "Host" and key != "Content-Length")
            }
            response = requests.request(
                method=request.method,
                url=target_url,
                headers=headers,
                json=request.data,
                params={key: value for key, value in request.GET.items()},
                allow_redirects=False,
            )

            # Return the response to the original request
            return HttpResponse(
                response.content,
                status=response.status_code,
                content_type=response.headers.get("Content-Type"),
            )
        except PermissionDenied:
            return HttpResponse(
                {},
                status=401,
            )
        except Exception as exc:
            response = self.handle_exception(exc)
            self.response = self.finalize_response(
                request, response, *args, **kwargs)
            return self.response
