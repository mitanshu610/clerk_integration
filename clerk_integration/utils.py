from pydantic import BaseModel, Field
import typing
from datetime import datetime
from fastapi import Request, HTTPException, status
from clerk_backend_api import Clerk
from clerk_backend_api.jwks_helpers import AuthenticateRequestOptions

class UserData(BaseModel):
    userId: typing.Union[int, str] = Field(..., alias="_id")
    orgId: typing.Optional[typing.Union[int, str]]
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


class UserDataHandler:
    def __init__(self, service_name, clerk_secret_key):
        self.service = service_name
        self.clerk_secret_key = clerk_secret_key
    
    async def get_user_data_from_request(self, request: Request):
        try:
            sdk = Clerk(bearer_auth=self.clerk_secret_key)
            request_state = sdk.authenticate_request(request,
                    AuthenticateRequestOptions()
            )
            if request_state.is_signed_in:
                user_id = request_state.payload['sub']
                org_id = request_state.payload['orgId']
                user_data = sdk.users.get(user_id=user_id)
                user_data = UserData(
                    _id=user_id,
                    orgId=org_id,
                    email=user_data.email_addresses[0].email_address,
                    firstName=user_data.first_name,
                    lastName=user_data.last_name
                )
                return user_data
            else:
                raise Exception()
        except Exception as e:
            raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "error": f"Session has expired in {self.service}",
                        "message": str(e),
                        "code": 6001
                    }
                ) from e