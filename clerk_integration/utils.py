from pydantic import BaseModel, Field
import typing
from datetime import datetime
from fastapi import Request

from clerk_integration.exceptions import UserDataException
from clerk_backend_api import Clerk
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

        if not request_state.is_signed_in:
            raise UserDataException(f"User is not signed in - Service - {self.service}")

        payload = request_state.payload
        public_metadata = payload.get('uPublicMetaData', {})
        if payload.get('orgId'):
            public_metadata = payload.get('oPublicMetaData', {})
                
        return UserData(
            _id=payload['sub'],
            orgId=payload.get('orgId'),
            email=payload.get('email'),
            firstName=payload.get('firstName'),
            lastName=payload.get('lastName'),
            roleSlug=payload.get('roleSlug'),
            publicMetadata=public_metadata
        )


    async def get_user_data_from_clerk(self, request: Request):
        try:
            user_data = await self._fetch_user_data(request)
            return user_data
        except UserDataException as e:
            raise e
        except Exception as e:
            raise UserDataException(f"Failed to get user data: {str(e)} - Service - {self.service}")
