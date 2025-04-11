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
    username: typing.Optional[str]
    phoneNumber: typing.Optional[str]
    roleSlug: typing.Optional[str]
    profilePicUrl: typing.Optional[str]
    active: typing.Optional[bool]
    roleIds: typing.Optional[list[int]]
    meta: typing.Optional[dict]
    createdAt: typing.Optional[datetime]
    updatedAt: typing.Optional[datetime]
    workspace: typing.List[typing.Dict]


class UserDataHanlder:
    def __init__(self, service_name, clerk_secret_key):
        self.service = service_name
        self.clerk_secret_key = clerk_secret_key
    
    async def get_user_data_from_request(self, request: Request):
        try:
            sdk = Clerk(bearer_auth=self.clerk_secret_key)
            request_state = sdk.authenticate_request(request)
            if request_state.is_signed_in:
                user_id = request_state.sessions[0].user.primary_identifier
                user_data = await sdk.user(user_id).get()
                return UserData.model_construct(user_data.dict())
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