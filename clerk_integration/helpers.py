from typing import Optional
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
        clerk_response = await self.clerk_client.users.list_async(request={"user_id": user_ids})
        clerk_users_by_id = {
            user.id: { 
                "firstName": user.first_name, "lastName": user.last_name, "email": user.email_addresses[0].email_address
            } for user in clerk_response
        }
        return clerk_users_by_id
    
    async def update_organization_metadata(self, organization_id: str, public_metadata: Optional[dict] = None, private_metadata: Optional[dict] = None):
        """
        Update organization metadata by merging existing values with the provided parameters.

        Args:
            organization_id (str): The ID of the organization for which metadata will be merged or updated.
            public_metadata (dict): Metadata visible to both frontend and backend.
            private_metadata (dict): Metadata visible only to the backend.

        Returns:
            dict: The response from the Clerk API after updating the metadata.
        """
        try:
            await self.clerk_client.organizations.merge_metadata_async(
                organization_id=organization_id, public_metadata=public_metadata, private_metadata=private_metadata
            )
            return True
        except Exception:
            return False
        
    async def update_user_metadata(self, user_id: str, public_metadata: Optional[dict] = None, private_metadata: Optional[dict] = None):  
        """  
        Update user metadata by merging existing values with the provided parameters.  
  
        Args:  
            user_id (str): The ID of the user for which metadata will be merged or updated.  
            public_metadata (dict): Metadata visible to both frontend and backend.  
            private_metadata (dict): Metadata visible only to the backend.  
  
        Returns:  
            dict: The response from the Clerk API after updating the metadata.  
        """  
        try:  
            await self.clerk_client.users.update_metadata_async(  
                user_id=user_id, public_metadata=public_metadata, private_metadata=private_metadata  
            )  
            return True
        except Exception:  
            return False
