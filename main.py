from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

from fastmcp import FastMCP, Context
from starlette.responses import PlainTextResponse
from starlette.middleware import Middleware
from starlette.requests import Request

# Import custom authentication middleware and token generation/matching utility
from wellaios.authenticate import (
    AuthenticationMiddleware,
    gen_user_auth_token,
    match_user_auth_token,
)

import uvicorn

# Initialize FastMCP application with a specific name for this demo
mcp = FastMCP("wellaios-demo")

# This special token indicates to WELLAIOS that user authorization is required
REQUEST_AUTH_TOKEN = "[AUTH]"

# In-memory dictionary to store user-specific secrets, keyed by their user ID
secrets: dict[str, str] = {}


@mcp.tool()
async def get_secret(ctx: Context) -> str:
    """
    Retrieves the secret previously set by the current user.

    This tool requires no parameters.
    """
    # Access the incoming HTTP request from the FastMCP context
    request = ctx.get_http_request()
    # Extract the user ID from the 'X-User-ID' header, which should be provided by the authentication middleware
    user_id = request.headers.get("X-User-ID")
    if user_id is None:
        # If no user ID is found, we fall back to a default user to support traditional MCP
        user_id = "single_user"
    if user_id not in secrets:
        # If the user has no secret stored, trigger the authorization process by returning a special token
        # and a newly generated user authentication token.
        return f"{REQUEST_AUTH_TOKEN} {gen_user_auth_token(user_id)}"
    print(secrets)
    # Return the user's secret if it exists
    return secrets[user_id]


@mcp.tool()
async def set_secret(secret: str, ctx: Context) -> str:
    """
    Sets a secret value for the current user.

    Args:
        secret: The string value that the user wishes to store as their secret.
    """
    # Access the incoming HTTP request from the FastMCP context
    request = ctx.get_http_request()
    # Extract the user ID from the 'X-User-ID' header. If not present, default to "unknown".
    user_id = request.headers.get("X-User-ID")
    if user_id is None:
        # If no user ID is found, we fall back to a default user to support traditional MCP
        user_id = "single_user"
    # Store the provided 'secret' string, keyed by the user's ID
    secrets[user_id] = secret
    return f"Secret set for user {user_id}"


# A custom route specifically designed for handling user authorization callbacks
@mcp.custom_route("/auth", methods=["GET"])
async def auth(request: Request):
    """
    Handles user authorization.

    This endpoint is invoked by WELLAIOS and is responsible for initiating or completing 
    the user authorization flow. For example, it might redirect the user to a third-party
    service like Google to obtain an access token, which can then be used to access the 
    user's data or services.
    """
    # Retrieve the 'userid' and 'token' from the request's query parameters
    user_id = request.query_params.get("userid")
    token = request.query_params.get("token")

    # Validate the user ID and token using the `match_user_auth_token` utility
    if user_id is None or token is None or not match_user_auth_token(user_id, token):
        # If validation fails (e.g., missing parameters or invalid token), return an Unauthorized response
        return PlainTextResponse("Unauthorized", status_code=401)

    # If the user ID is not yet in our secrets dictionary, initialize an empty secret for them.
    # This effectively registers the user in our system.
    if user_id not in secrets:
        secrets[user_id] = ""
    # Once the user is successfully authorized and potentially registered, return an OK response
    return PlainTextResponse("User authorized", status_code=200)


if __name__ == "__main__":
    # Define the list of custom middleware to be applied to the HTTP application.
    custom_middleware = [Middleware(AuthenticationMiddleware)]
    # Create the FastMCP HTTP application instance, applying the configured middleware
    http_app = mcp.http_app(middleware=custom_middleware)
    # Run the Uvicorn server, making the application accessible on all network interfaces
    # at port 30000.
    uvicorn.run(http_app, host="0.0.0.0", port=30000)
