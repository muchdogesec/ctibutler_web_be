import typing

from django.http import HttpRequest
from rest_framework_api_key.permissions import BaseHasAPIKey

from apps.api.models import UserAPIKey
from apps.teams.models import TeamApiKey
from apps.teams.helpers import get_team_from_request


class HasTeamApiKey(BaseHasAPIKey):
    model = TeamApiKey

    def has_permission(self, request: HttpRequest, view: typing.Any) -> bool:
        has_perm = super().has_permission(request, view)
        print(has_perm)
        if has_perm:
            team = get_team_from_request(request)
            view.team = team
            request.team = team
            return True
        return has_perm
