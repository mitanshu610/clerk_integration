from clerk_backend_api import Clerk

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
