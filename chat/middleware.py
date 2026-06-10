from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from rest_framework.authtoken.models import Token


@database_sync_to_async
def get_user(token_key):
    try:
        token = Token.objects.select_related("user").get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        return AnonymousUser()


class TokenAuthMiddleware:

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):

        headers = dict(scope["headers"])

        auth_header = headers.get(b"authorization")

        scope["user"] = AnonymousUser()

        if auth_header:

            auth_header = auth_header.decode()

            auth_parts = auth_header.split()

            if len(auth_parts) == 2:

                token_key = auth_parts[1]

                scope["user"] = await get_user(token_key)

        return await self.inner(scope, receive, send)