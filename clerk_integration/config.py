from typing import Optional, Dict
from clerk_backend_api import Clerk, models

import aiohttp


class ClerkHelper:
    """
    A class for managing Clerk authentications
    """

    BASE_URL = "https://api.clerk.com/v1"

    def __init__(self, api_key: str):
        """
        Initialize the ClerkOrganizationManager with your Clerk API key.

        Args:
            api_key (str): Your Clerk secret API key in the format sk_<environment>_<secret value>
        """
        self.clerk_secret_key = api_key
        self.clerk_client = Clerk(bearer_auth=self.clerk_secret_key)
    
    async def refresh_token(self, session_id: str) -> Dict:
        """
        Refresh the session token using Clerk's backend SDK.

        Args:
            session_id (str): The ID of the session to refresh

        Returns:
            Dict: The refreshed session data

        Raises:
            Exception: If the refresh operation fails
        """
        try:
            session_token = await self.clerk_client.sessions.create_token_from_template_async(session_id=session_id, template_name="neon")
            return session_token
        except Exception as e:
            raise Exception(f"Failed to refresh token: {str(e)}")