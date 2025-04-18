from pydantic import BaseModel, Field
import typing
from datetime import datetime
from fastapi import Request
from clerk_integration.exceptions import UserDataException
from clerk_backend_api import Clerk, models
from clerk_backend_api.jwks_helpers import AuthenticateRequestOptions

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

class ClerkAuthHelper:
    def __init__(self, service_name, clerk_secret_key):
        self.service = service_name
        self.clerk_secret_key = clerk_secret_key

    async def _fetch_user_data(self, request: Request) -> UserData:
        sdk = Clerk(bearer_auth=self.clerk_secret_key)
        request_state = sdk.authenticate_request(request, AuthenticateRequestOptions())
        if request_state.is_signed_in:
            user_id = request_state.payload['sub']
            org_id = request_state.payload['orgId']
            user_data = sdk.users.get(user_id=user_id)
            return UserData(
                _id=user_id,
                orgId=org_id,
                email=user_data.email_addresses[0].email_address,
                firstName=user_data.first_name,
                lastName=user_data.last_name
            )
        else:
            raise UserDataException("User is not signed in")

    async def get_user_data_from_clerk(self, request: Request):
        try:
            return await self._fetch_user_data(request)
        except UserDataException as e:
            raise e
        except Exception as e:
            raise UserDataException(f"Failed to get user data: {str(e)}")