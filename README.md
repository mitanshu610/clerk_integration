# Clerk Integration

A Python package that provides helper utilities for integrating Clerk authentication services with FastAPI applications.

## Installation

```bash
pip install clerk_integration
```

## Requirements

- Python >= 3.9
- clerk-backend-api >= 1.8.0
- fastapi >= 0.115.3
- pydantic >= 2.11.3
- aiohttp >= 3.10.11

## Features

- User data fetching and management
- Organization metadata management
- Clerk authentication helpers
- FastAPI integration utilities

## Quick Start

```python
from fastapi import FastAPI, Request
from clerk_integration.utils import ClerkAuthHelper
from clerk_integration.helpers import ClerkHelper

app = FastAPI()
clerk_auth = ClerkAuthHelper("your-service-name", "your-clerk-secret-key")
clerk_helper = ClerkHelper("your-clerk-secret-key")

@app.get("/user")
async def get_user(request: Request):
    user_data = await clerk_auth.get_user_data_from_clerk(request)
    return user_data

@app.get("/users")
async def get_users(user_ids: list[str]):
    users = await clerk_helper.get_clerk_users_by_id(user_ids)
    return users
```

## API Reference

### ClerkAuthHelper

Helper class for handling Clerk authentication in FastAPI applications.

```python
clerk_auth = ClerkAuthHelper(service_name, clerk_secret_key)
```

Methods:
- `get_user_data_from_clerk(request)`: Fetches authenticated user data from Clerk

### ClerkHelper

Utility class for managing Clerk users and organizations.

```python
clerk_helper = ClerkHelper(api_key)
```

Methods:
- `get_clerk_users_by_id(user_ids)`: Retrieve multiple users by their IDs
- `update_organization_metadata(organization_id, public_metadata, private_metadata)`: Update organization metadata
- `update_user_metadata(user_id, public_metadata, private_metadata)`: Update user metadata

## License

MIT License

## Author

Mitanshu Bhatt (mitubhatt670@gmail.com)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
