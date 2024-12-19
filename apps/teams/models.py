import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext

from apps.api.models import AbstractAPIKey
from apps.utils.models import BaseModel
from apps.subscriptions.models import SubscriptionModelBase

from . import roles


class Team(BaseModel, SubscriptionModelBase):
    """
    A Team, with members.
    """

    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    slug = models.SlugField(null=True, blank=True)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="teams", through="Membership"
    )
    is_private = models.BooleanField(default=False)

    # your team customizations go here.

    def __str__(self):
        return self.name

    def get_user_limit(self):
        if not self.active_stripe_subscription:
            return 0
        return int(self.subscription.plan.product.metadata.get('allowed_user_count', 0))

    def get_allowed_api_access(self):
        if not self.active_stripe_subscription:
            return False
        return self.subscription.plan.product.metadata.get('allowed_api_access', '') == 'true'

    @property
    def allowed_api_access(self):
        return self.get_allowed_api_access()
    
    @property
    def user_limit(self):
        return self.get_user_limit()

    @property
    def email(self):
        return self.membership_set.filter(role=roles.ROLE_ADMIN).first().user.email

    @property
    def sorted_memberships(self):
        return self.membership_set.order_by("user__email")

    def pending_invitations(self):
        return self.invitations.filter(is_accepted=False)


class Membership(BaseModel):
    """
    A user's team membership
    """

    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=100, choices=roles.ROLE_CHOICES)
    # your additional membership fields go here.

    def __str__(self):
        return f"{self.user}: {self.team}"

    def is_admin(self) -> bool:
        return self.role == roles.ROLE_ADMIN

    def is_owner(self) -> bool:
        return self.role == roles.ROLE_OWNER

    class Meta:
        # Ensure a user can only be associated with a team once.
        unique_together = ("team", "user")


class Invitation(BaseModel):
    """
    An invitation for new team members.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="invitations")
    email = models.EmailField()
    role = models.CharField(
        max_length=100, choices=roles.ROLE_CHOICES, default=roles.ROLE_MEMBER
    )
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_invitations",
    )
    is_accepted = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    accepted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="accepted_invitations",
        null=True,
        blank=True,
    )

    def get_url(self) -> str:
        link = settings.INVITATION_URL + str(self.id)
        print(link)
        return link


class BaseTeamModel(BaseModel):
    """
    Abstract model for objects that are part of a team.

    See `teams_example` app for usage.
    """

    team = models.ForeignKey(
        Team, verbose_name=gettext("Team"), on_delete=models.CASCADE
    )

    class Meta:
        abstract = True


class TeamApiKeyStatus:
    BLOCKED = 'blocked'
    ACTIVE = 'active'

class TeamApiKey(AbstractAPIKey):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    status = models.CharField(max_length=10, default=TeamApiKeyStatus.ACTIVE)
    key_id = models.UUIDField(blank=True, null=True)
    last_used = models.DateTimeField(blank=True, null=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE)
    clear_key = models.CharField(max_length=100, blank=True, null=True)
