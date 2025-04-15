from clerk_backend_api import Clerk

import aiohttp


class ClerkHelper:
    """
    A class for managing Clerk authentications
    """

    def __init__(self, api_key: str):
        """
        Initialize the ClerkOrganizationManager with your Clerk API key.

        Args:
            api_key (str): Your Clerk secret API key in the format sk_<environment>_<secret value>
        """
        self.clerk_secret_key = api_key
        self.clerk_client = Clerk(bearer_auth=self.clerk_secret_key)
    
    
    async def get_clerk_users_by_id(self, user_ids):
        """
        Retrieve Clerk users by their IDs.

        Args:
            user_ids (list): A list of user IDs to retrieve.

        Returns:
            dict: A dictionary of users keyed by their ID.
        """
        clerk_response = self.clerk_client.users.list(request={"user_id": user_ids})
        clerk_users_by_id = {user["id"]: user for user in clerk_response["data"]}
        return clerk_users_by_id
