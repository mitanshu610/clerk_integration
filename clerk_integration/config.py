from typing import Optional, Dict

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
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    async def patch_organization_metadata(
            self,
            organization_id: str,
            public_metadata: Optional[Dict] = None,
            private_metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Update organization metadata attributes by merging existing values with the provided parameters.
        Deep merges any nested JSON objects. Set a key to null to remove it.

        Args:
            organization_id (str): The ID of the organization to update
            public_metadata (Dict, optional): Metadata visible to frontend and backend
            private_metadata (Dict, optional): Metadata only visible to backend

        Returns:
            Dict: The updated organization data

        Raises:
            aiohttp.ClientResponseError: If the API request fails
        """
        url = f"{self.BASE_URL}/organizations/{organization_id}/metadata"

        # Build payload with only the provided metadata fields
        payload = {}
        if public_metadata is not None:
            payload["public_metadata"] = public_metadata
        if private_metadata is not None:
            payload["private_metadata"] = private_metadata

        if not payload:
            raise ValueError("At least one of public_metadata or private_metadata must be provided")

        async with aiohttp.ClientSession() as session:
            async with session.patch(url, headers=self.headers, json=payload) as response:
                response.raise_for_status()
                return await response.json()