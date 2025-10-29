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
        self.base_url = "https://api.clerk.com/v1"
    
    
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
    
    async def get_org_members(self, organization_id: str, query: Optional[str] = None, limit: int = 10, offset: int = 0, user_id: Optional[str] = None):
        """
        Retrieve all members of an organization with optional filtering using aiohttp.

        Args:
            organization_id (str): The organization ID.
            query (str, optional): Search query to filter members. Matches against email, phone, username, 
                                 web3 wallet, user ID, first and last names.
            limit (int, optional): Number of results to return. Defaults to 10. Max 500.
            offset (int, optional): Number of results to skip. Defaults to 0.

        Returns:
            dict: Organization members matching the query parameters.
        """
        endpoint = f"{self.base_url}/organizations/{organization_id}/memberships"
        
        headers = {
            "Authorization": f"Bearer {self.clerk_secret_key}",
            "Content-Type": "application/json"
        }
        
        params = {
            "limit": min(limit, 500),
            "offset": max(offset, 0)
        }
        
        if query:
            params["query"] = query
        
        if user_id:
            params["user_id"] = [user_id]

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(endpoint, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        members = []
                        for member in data["data"]:
                            user_id = member["public_user_data"]["user_id"]
                            first_name = member["public_user_data"].get("first_name")
                            last_name = member["public_user_data"].get("last_name")
                            
                            member_data = {
                                "id": user_id,
                                "firstName": first_name,
                                "lastName": last_name,
                                "role": member.get("role")
                            }
                            
                            # Check if firstname or lastname is null/None, then fetch email
                            if first_name is None or last_name is None:
                                try:
                                    user_details = await self.clerk_client.users.get_async(user_id=user_id)
                                    if user_details and user_details.email_addresses:
                                        member_data["email"] = user_details.email_addresses[0].email_address
                                except Exception:
                                    # If fetching user details fails, continue without email
                                    pass
                            
                            members.append(member_data)
                        
                        return {
                            "members": members,
                            "total_count": data.get("total_count", 0)
                        }
                    else:
                        error_data = await response.json()
                        return {
                            "error": f"API request failed: {error_data.get('message', 'Unknown error')}",
                            "status": response.status,
                            "members": [],
                            "total_count": 0
                        }
            except aiohttp.ClientError as e:
                return {
                    "error": f"Network error: {str(e)}",
                    "members": [],
                    "total_count": 0
                }
            except Exception as e:
                return {
                    "error": f"Unexpected error: {str(e)}",
                    "members": [],
                    "total_count": 0
                }
    
    async def update_organization_config(self, organization_id: str, max_allowed_memberships: int = 5) -> bool:
        try:
            await self.clerk_client.organizations.update_async(
                organization_id=organization_id, max_allowed_memberships=max_allowed_memberships
            )
            return True
        except Exception:
            return False

    async def get_user_org_membership(self, user_id: str, organization_id: str):
        """
        Retrieve user membership details for a specific organization.
        
        Args:
            user_id (str): The ID of the user to check membership for.
            organization_id (str): The ID of the organization.
            
        Returns:
            OrganizationMembership: The membership object if user is a member.
            dict: Error dictionary if user is not a member or if an error occurs.
        """
        try:
            membership = await self.clerk_client.organization_memberships.list_async(
                organization_id=organization_id, user_id=[user_id]
            )
            return membership.data[0]
        except IndexError:
            return {
                "error": f"User with user_id '{user_id}' is not a member of organization '{organization_id}'"
            }
        except Exception as e:
            return {
                "error": f"Unexpected error: {str(e)}"
            }