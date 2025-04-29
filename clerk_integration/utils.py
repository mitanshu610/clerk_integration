from pydantic import BaseModel, Field
import typing
from datetime import datetime
from fastapi import Request

from clerk_integration.exceptions import UserDataException
from clerk_backend_api import Clerk, models
from clerk_backend_api.jwks_helpers import AuthenticateRequestOptions
from clerk_integration.helpers import ClerkHelper
from contextlib import asynccontextmanager
from urllib.parse import urlparse

import redis.asyncio as redis

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
    def __init__(self, service_name, clerk_secret_key, redis_url=None):
        self.service = service_name
        self.clerk_secret_key = clerk_secret_key
        self.clerk_helper = ClerkHelper(clerk_secret_key)

    async def _fetch_user_data(self, request: Request) -> UserData:
        sdk = Clerk(bearer_auth=self.clerk_secret_key)
        request_state = sdk.authenticate_request(request, AuthenticateRequestOptions())
        if request_state.is_signed_in:
            user_id = request_state.payload['sub']
            org_id = request_state.payload['orgId']
            first_name = request_state.payload['firstName']
            last_name = request_state.payload['lastName']
            primary_email = request_state.payload['email']
            public_metadata = {}
            if request_state.payload['uPublicMetaData']:
                public_metadata = request_state.payload['uPublicMetaData']

            if org_id and request_state.payload['oPublicMetaData']:
                public_metadata = request_state.payload['oPublicMetaData']

            role_slug = request_state.payload['roleSlug']
                    
            return UserData(
                _id=user_id,
                orgId=org_id,
                email=primary_email,
                firstName=first_name,
                lastName=last_name,
                roleSlug=role_slug,
                publicMetadata=public_metadata
            )
        else:
            raise UserDataException(f"User is not signed in - Service - {self.service}")

    async def get_user_data_from_clerk(self, request: Request):
        try:
            user_data = await self._fetch_user_data(request)
            return user_data
        except UserDataException as e:
            raise e
        except Exception as e:
            raise UserDataException(f"Failed to get user data: {str(e)} - Service - {self.service}")
