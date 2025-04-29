from pydantic import BaseModel, Field
import typing
from datetime import datetime
from fastapi import Request
from clerk_integration.exceptions import UserDataException
from clerk_backend_api import Clerk, models
from clerk_backend_api.jwks_helpers import AuthenticateRequestOptions
from clerk_integration.helpers import ClerkHelper

class UserData(BaseModel):
    userId: typing.Union[int, str] = Field(..., alias="_id")
    orgId: typing.Optional[typing.Union[int, str]] = None
    firstName: typing.Optional[str]
    lastName: typing.Optional[str]
    email: typing.Optional[str]
    username: typing.Optional[str] = None
    phoneNumber: typing.Optional[str] = None
    roleSlug: typing.Optional[str] = None
    profilePicUrl: typing.Optional[str] = None
    active: typing.Optional[bool] = None
    roleIds: typing.Optional[list[int]] = None
    meta: typing.Optional[dict] = None
    createdAt: typing.Optional[datetime] = None
    updatedAt: typing.Optional[datetime] = None
    workspace: typing.Optional[typing.List[typing.Dict]] = None
    publicMetadata: typing.Optional[typing.Dict] = None

class ClerkAuthHelper:
    def __init__(self, service_name, clerk_secret_key):
        self.service = service_name
        self.clerk_secret_key = clerk_secret_key
        self.clerk_helper = ClerkHelper(clerk_secret_key)

    async def _fetch_user_data(self, request: Request) -> UserData:
        sdk = Clerk(bearer_auth=self.clerk_secret_key)
        request_state = sdk.authenticate_request(request, AuthenticateRequestOptions())
        if request_state.is_signed_in:
            user_id = request_state.payload['sub']
            org_id = request_state.payload['orgId']
            user_data = await sdk.users.get_async(user_id=user_id)
            role_slug = None
            if org_id:
                org_entries = await self.clerk_helper.get_org_members(org_id, user_id=user_id)
                member = org_entries["members"]
                if member:
                    role_slug = member[0].get("role", None)
                    
            return UserData(
                _id=user_id,
                orgId=org_id,
                email=user_data.email_addresses[0].email_address,
                firstName=user_data.first_name,
                lastName=user_data.last_name,
                roleSlug=role_slug,
                publicMetadata=user_data.public_metadata
            )
        else:
            raise UserDataException(f"User is not signed in - Service - {self.service}")

    async def get_user_data_from_clerk(self, request: Request):
        try:
            return await self._fetch_user_data(request)
        except UserDataException as e:
            raise e
        except Exception as e:
            raise UserDataException(f"Failed to get user data: {str(e)} - Service - {self.service}")