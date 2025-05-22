import logging
import requests
from auth_manager import RedEnergyAuth


auth = RedEnergyAuth()

def get_access_token():
    try:
        logging.debug("Retrieving access token...")
        token = auth.get_access_token()
        logging.debug("Access token retrieved successfully.")
        return token
    except Exception as e:
        logging.error(f"Failed to retrieve access token: {e}")
        raise

def call_customer_api():
    try:
        logging.info("Calling customer API...")
        access_token = get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        resp = requests.get("https://selfservice.services.retail.energy/v1/customers/current", headers=headers)
        resp.raise_for_status()
        logging.info("Customer API call successful.")
        return resp.json()
    except requests.RequestException as e:
        logging.error(f"Customer API request failed: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error in call_customer_api: {e}")
        raise

def call_properties_api():
    try:
        logging.info("Calling properties API...")
        access_token = get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        resp = requests.get("https://selfservice.services.retail.energy/v1/properties", headers=headers)
        resp.raise_for_status()
        logging.info("Properties API call successful.")
        return resp.json()
    except requests.RequestException as e:
        logging.error(f"Properties API request failed: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error in call_properties_api: {e}")
        raise

def call_usage_interval_api(consumer_number, from_date, to_date):
    try:
        logging.info(f"Calling usage interval API for consumer {consumer_number} from {from_date} to {to_date}...")
        access_token = get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {
            "fromDate": from_date,
            "toDate": to_date,
            "consumerNumber": consumer_number
        }
        resp = requests.get("https://selfservice.services.retail.energy/v1/usage/interval", headers=headers, params=params)
        resp.raise_for_status()
        logging.info("Usage interval API call successful.")
        return resp.json()
    except requests.RequestException as e:
        logging.error(f"Usage interval API request failed: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error in call_usage_interval_api: {e}")
        raise
