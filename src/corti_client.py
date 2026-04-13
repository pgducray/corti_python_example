import requests
import os
from typing import Optional, Dict

class CortiClient:
    """
    Base Corti API client with authentication and common utilities.

    This class handles:
    - Authentication via OAuth2 Client Credentials
    - Environment configuration
    - Common header generation
    """

    def __init__(self):
        """Initialize the CortiClient by pulling credentials from the environment."""
        self.tenant_name = os.getenv("CORTI_TENANT_NAME")
        self.client_id = os.getenv("CORTI_CLIENT_ID")
        self.client_secret = os.getenv("CORTI_CLIENT_SECRET")
        self.environment = os.getenv("CORTI_ENVIRONMENT", "eu")

        # Auth URL - Corti uses Keycloak with realm pattern
        self.auth_url = f"https://auth.{self.environment}.corti.app/realms/{self.tenant_name}/protocol/openid-connect/token"
        # Fallback auth URL patterns (older formats)
        self.fallback_auth_urls = [
            f"https://auth.{self.environment}.corti.app/oauth2/token",
            f"https://{self.tenant_name}.{self.environment}.auth.corti.app/oauth2/token"
        ]

        # API URL - Corti uses api.{environment}.corti.app/v2
        self.api_url = f"https://api.{self.environment}.corti.app/v2"

        self.access_token: Optional[str] = None

    def is_configured(self) -> bool:
        """Check if all required credentials are present."""
        return bool(self.tenant_name and self.client_id and self.client_secret)

    def authenticate(self) -> str:
        """
        Authenticate via Client Credentials flow.
        Returns the access token and caches it.
        """
        if not self.is_configured():
            raise ValueError("Credentials missing. Check your .env file.")

        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "audience": "capioswe"
        }

        # Try primary auth URL
        last_error = None
        try:
            response = requests.post(self.auth_url, data=payload, timeout=10)
            response.raise_for_status()
            self.access_token = response.json().get("access_token")
            return self.access_token
        except requests.exceptions.RequestException as e:
            last_error = e

        # Try all fallback URLs
        for fallback_url in self.fallback_auth_urls:
            try:
                response = requests.post(fallback_url, data=payload, timeout=10)
                response.raise_for_status()
                self.access_token = response.json().get("access_token")
                return self.access_token
            except requests.exceptions.RequestException as e:
                last_error = e
                continue

        # All attempts failed
        raise Exception(
            f"Failed to authenticate using all available auth URLs. "
            f"Last error: {last_error}"
        )

    def get_headers(self, include_tenant: bool = False) -> Dict[str, str]:
        """
        Return the headers required for API calls.

        Args:
            include_tenant: If True, includes Tenant-Name header

        Returns:
            Dictionary of headers
        """
        if not self.access_token:
            self.authenticate()

        headers = {"Authorization": f"Bearer {self.access_token}"}

        if include_tenant:
            headers["Tenant-Name"] = self.tenant_name

        return headers
