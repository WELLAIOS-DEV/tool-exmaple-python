import os
from typing import Any, Awaitable, Callable, MutableMapping
from starlette.responses import PlainTextResponse

# Retrieve the main authentication token from environment variables.
# This token is used for general API access, not specific user authorization.
BEARER_TOKEN = os.environ.get("AUTH_TOKEN")

# A dictionary used for short-term storage of user-specific OAuth tokens.
# This acts as a temporary memory to link a user ID with a generated authentication token
# during the authorization flow.
temp_user_oauth_token: dict[str, str] = {}


class AuthenticationMiddleware:
    """
    A Starlette middleware for handling authentication based on a bearer token.

    This middleware intercepts incoming HTTP requests. It checks for an Authorization
    header with a Bearer token for most routes. For the "/auth" route, it expects
    'userid' and 'token' as query parameters to validate user-specific authorization.
    """

    def __init__(
        self,
        app: Callable[
            [
                MutableMapping[str, Any],
                Callable[[], Awaitable[MutableMapping[str, Any]]],
                Callable[[MutableMapping[str, Any]], Awaitable[None]],
            ],
            Awaitable[None],
        ],
    ):
        """
        Initializes the AuthenticationMiddleware.

        Args:
            app: The ASGI application to be wrapped by this middleware.
        """
        self.app = app

    async def __call__(
        self,
        scope: MutableMapping[str, Any],
        receive: Callable[[], Awaitable[MutableMapping[str, Any]]],
        send: Callable[[MutableMapping[str, Any]], Awaitable[None]],
    ):
        """
        The ASGI callable method for the middleware.

        Args:
            scope: The ASGI scope dictionary containing information about the request.
            receive: An awaitable callable that receives incoming messages.
            send: An awaitable callable that sends outgoing messages.
        """
        # Process only HTTP requests
        if scope["type"] == "http":
            # Get the request path from the scope, default to "/"
            path = scope.get("path", "/")

            # Extract and decode headers into a dictionary for easy access
            headers = scope.get("headers", [])
            header_dict = {
                header[0].decode("latin-1").lower(): header[1].decode("latin-1")
                for header in headers
            }

            # Initialize the expected token with the general BEARER_TOKEN
            target_token = BEARER_TOKEN
            # Initialize bearer token from request
            bearer = None

            # Special handling for the "/auth" path
            if path.startswith("/auth"):
                # Decode the query string and parse query parameters
                query_string = scope.get("query_string", b"").decode("latin-1")
                query_params = {}
                if query_string:
                    for item in query_string.split("&"):
                        if "=" in item:
                            key, value = item.split("=", 1)
                            query_params[key] = value
                        elif item:
                            query_params[item] = ""  # Handle parameters without a value

                # Get the user ID from query parameters
                user_id = query_params.get("userid", "")
                # For /auth path, the target token is the temporary user-specific token
                target_token = temp_user_oauth_token.get(user_id)
                # The bearer token for /auth path comes from the 'token' query parameter
                bearer = query_params.get("token")
            else:
                # For all other paths, check the 'Authorization' header
                authorization_header = header_dict.get("authorization")

                # If no Authorization header is present, return 401 Unauthorized
                if not authorization_header:
                    response = PlainTextResponse(
                        "Missing Authorization Header", status_code=401
                    )
                    await response(scope, receive, send)
                    return

                # Parse the Authorization header to extract the bearer token
                parts = authorization_header.strip().split(maxsplit=1)
                if len(parts) == 2 and parts[0].lower() == "bearer":
                    bearer = parts[1]

            # If the extracted bearer token does not match the target token (either general or user-specific)
            if target_token is None or bearer != target_token:
                # Return 401 Unauthorized response
                response = PlainTextResponse("Unauthorized", status_code=401)
                await response(scope, receive, send)
                return

            # If authentication is successful, proceed to the next ASGI application in the stack
            await self.app(scope, receive, send)
        else:
            # If it's not an HTTP scope (e.g., websocket), just pass it to the next application
            await self.app(scope, receive, send)


def gen_user_auth_token(user_id: str) -> str:
    """
    Generates a cryptographically secure random token for a given user ID
    and stores it temporarily.

    Args:
        user_id: The unique identifier for the user.

    Returns:
        A hexadecimal string representing the generated token.
    """
    # Generate a random 32-byte token and convert it to a hexadecimal string
    random_token = os.urandom(32).hex()
    # Store the generated token in the temporary dictionary, keyed by user ID
    temp_user_oauth_token[user_id] = random_token
    return random_token


def match_user_auth_token(user_id: str, token: str) -> bool:
    """
    Compares a provided token with the temporarily stored token for a given user ID.

    Args:
        user_id: The unique identifier for the user.
        token: The token to be validated.

    Returns:
        True if the provided token matches the stored token for the user, False otherwise.
    """
    # Check if the user ID exists in the temporary token storage
    if user_id in temp_user_oauth_token:
        # Compare the provided token with the stored token for the user
        return temp_user_oauth_token[user_id] == token
    return False
