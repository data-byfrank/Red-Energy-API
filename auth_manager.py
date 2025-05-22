import logging
import os
import datetime
import dotenv
import requests
import uuid
from urllib.parse import urlparse, parse_qs

from authlib.integrations.requests_client import OAuth2Session
from authlib.common.security import generate_token
from authlib.oauth2.rfc7636 import create_s256_code_challenge

# Load environment variables
dotenv.load_dotenv()


DISCOVERY_URL = "https://login.redenergy.com.au/oauth2/default/.well-known/openid-configuration"
REDIRECT_URI = "au.com.redenergy://callback"

class RedEnergyAuth:
    def __init__(self, env_file=".env"):
        self.env_file = env_file
        dotenv.load_dotenv(dotenv_path=env_file, override=True)
        self.username = os.getenv("RE_USERNAME")
        self.password = os.getenv("RE_PASSWORD")
        self.client_id = os.getenv("RE_CLIENT_ID")

    def update_env_var(self, key, value):
        try:
            with open(self.env_file, "r") as f:
                lines = f.readlines()
        except FileNotFoundError:
            lines = []

        new_lines, updated = [], False
        for line in lines:
            if line.startswith(f"{key}="):
                new_lines.append(f"{key}={value}\n")
                updated = True
            else:
                new_lines.append(line)

        if not updated:
            new_lines.append(f"{key}={value}\n")

        with open(self.env_file, "w") as f:
            f.writelines(new_lines)

        dotenv.load_dotenv(dotenv_path=self.env_file, override=True)
        logging.debug(f"Updated {key}")

    def delete_env_var(self, key):
        try:
            with open(self.env_file, "r") as f:
                lines = f.readlines()
        except FileNotFoundError:
            lines = []

        new_lines = [line for line in lines if not line.startswith(f"{key}=")]
        with open(self.env_file, "w") as f:
            f.writelines(new_lines)

        dotenv.load_dotenv(dotenv_path=self.env_file, override=True)
        logging.debug(f"Deleted {key}")

    def is_token_valid(self):
        expiry = os.getenv("RE_ACCESS_TOKEN_EXPIRES_AT")
        try:
            return datetime.datetime.fromisoformat(expiry) > datetime.datetime.now()
        except Exception as e:
            logging.debug(f"Token expiry error: {e}")
            return False

    def get_session_token(self):
        payload = {
            "username": self.username,
            "password": self.password,
            "options": {
                "warnBeforePasswordExpired": False,
                "multiOptionalFactorEnroll": False
            }
        }
        resp = requests.post("https://redenergy.okta.com/api/v1/authn", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["sessionToken"], data["expiresAt"]

    def get_oauth_endpoints(self):
        resp = requests.get(DISCOVERY_URL)
        resp.raise_for_status()
        data = resp.json()
        return data["authorization_endpoint"], data["token_endpoint"]

    def establish_session(self):
        if os.getenv("RE_ACCESS_TOKEN") and self.is_token_valid():
            logging.debug("Valid token found.")
            return os.getenv("RE_ACCESS_TOKEN")

        auth_url, token_url = self.get_oauth_endpoints()
        refresh_token = os.getenv("RE_REFRESH_TOKEN")

        if refresh_token:
            try:
                client = OAuth2Session(
                    client_id=self.client_id,
                    token={
                        'refresh_token': refresh_token,
                        'access_token': os.getenv("RE_ACCESS_TOKEN"),
                        'expires_at': datetime.datetime.fromisoformat(
                            os.getenv("RE_ACCESS_TOKEN_EXPIRES_AT")
                        ).timestamp(),
                    }
                )
                token = client.refresh_token(token_url, refresh_token=refresh_token)
                self._save_token(token)
                logging.debug("Refreshed token.")
                return token["access_token"]
            except Exception as e:
                logging.warning(f"Refresh failed: {e}")

        if not self.username or not self.password or not self.client_id:
            raise ValueError("Missing credentials in .env")

        session_token, expires_at = self.get_session_token()
        self.update_env_var("RE_SESSION_TOKEN", session_token)
        self.update_env_var("RE_SESSION_TOKEN_EXPIRES_AT", expires_at)

        # Generate PKCE values manually
        code_verifier = generate_token(48)
        code_challenge = create_s256_code_challenge(code_verifier)
        self.update_env_var("RE_CODE_VERIFIER", code_verifier)

        client = OAuth2Session(
            client_id=self.client_id,
            redirect_uri=REDIRECT_URI,
            scope="openid profile offline_access"
        )

        state, nonce = str(uuid.uuid4()), str(uuid.uuid4())
        extra = {
            "sessionToken": session_token,
            "state": state,
            "nonce": nonce,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256"
        }

        auth_url_full, _ = client.create_authorization_url(auth_url, **extra)
        logging.debug(f"Go to:\n{auth_url_full}")

        # Simulate redirect manually
        r = requests.get(auth_url_full, allow_redirects=False)
        location = r.headers.get("Location", "")
        code = parse_qs(urlparse(location).query).get("code", [None])[0]

        if not code:
            raise RuntimeError("Auth code not found")

        token = client.fetch_token(
            token_url,
            code=code,
            code_verifier=code_verifier,
            include_client_id=True,
        )
        self._save_token(token)
        return token["access_token"]

    def _save_token(self, token):
        self.update_env_var("RE_ACCESS_TOKEN", token["access_token"])
        self.update_env_var("RE_ACCESS_TOKEN_EXPIRES_AT", (
            datetime.datetime.now() + datetime.timedelta(seconds=token["expires_in"])
        ).isoformat())
        if "refresh_token" in token:
            self.update_env_var("RE_REFRESH_TOKEN", token["refresh_token"])
        self.delete_env_var("RE_AUTH_CODE")
        self.delete_env_var("RE_CODE_VERIFIER")

    def get_access_token(self):
        return self.establish_session()
