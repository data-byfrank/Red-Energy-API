from datetime import datetime, timedelta
from zoneinfo import ZoneInfo 
from energy_api import call_customer_api, call_properties_api, call_usage_interval_api
from db_manager import init_db, get_all_usage_data, update_usage_data, update_customer_data, update_property_data
import os
import logging
import dotenv

dotenv.load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("redenergy_usage_data.log"),
        logging.StreamHandler()
    ]
)

STATE_TIMEZONES = {
    "NSW": "Australia/Sydney",
    "VIC": "Australia/Melbourne",
    "QLD": "Australia/Brisbane",
    "SA":  "Australia/Adelaide",
    "WA":  "Australia/Perth",
    "TAS": "Australia/Hobart",
    "NT":  "Australia/Darwin",
    "ACT": "Australia/Sydney",  
}

preload_usage_days = int(os.getenv("PRELOAD_USAGE_DAYS", 28))  # Default to 28 days if not set

def get_timezone_by_sate(state: str):
    try:
        state = state.strip().upper()
        timezone = ZoneInfo(STATE_TIMEZONES.get(state))
        if not timezone:
            raise ValueError(f"Unknown or unsupported state: {state}")
        return timezone
    except Exception as e:
        logging.error(f"Failed to determine timezone for state '{state}': {e}")
        raise

def refresh_usage(consumerNumber, propertyNumber, tz):
    try:
        logging.info(f"Refreshing usage for consumer {consumerNumber}, property {propertyNumber}")
        existing_usage = get_all_usage_data()
        logging.debug(f"Existing usage record count: {len(existing_usage)}")

        if existing_usage:
            latest_date_str = (datetime.strptime(max(item['usage_date'] for item in existing_usage), "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
            from_date = (datetime.strptime(latest_date_str, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
            to_date = datetime.now(tz).strftime("%Y-%m-%d")
            logging.info(f"Fetching usage from {from_date} to {to_date}")
        else:
            from_date = (datetime.now(tz) - timedelta(days=preload_usage_days)).strftime("%Y-%m-%d")
            to_date = datetime.now(tz).strftime("%Y-%m-%d")
            logging.info(f"No existing usage data. Preloading from {from_date} to {to_date}")

        usage_data = call_usage_interval_api(consumerNumber, from_date, to_date)

        for day_data in usage_data:
            date = day_data["usageDate"]
            update_usage_data(consumerNumber, propertyNumber, date, day_data)
            logging.debug(f"Updated usage for {date}")

    except Exception as e:
        logging.error(f"Failed to refresh usage for consumer {consumerNumber}, property {propertyNumber}: {e}")

def main():
    try:
        logging.info("Initializing database")
        init_db()

        logging.info("Fetching customer data")
        customerData = call_customer_api()
        customerNumber = customerData["customerNumber"]
        update_customer_data(customerNumber, customerData)
        logging.debug(f"Customer data updated for {customerNumber}")

        logging.info("Fetching property data")
        properties = call_properties_api()
        for property in properties:
            propertyNumber = property["propertyNumber"]
            update_property_data(propertyNumber, property)
            logging.debug(f"Property data updated for {propertyNumber}")

        customerAccounts = customerData["accounts"]
        for account in customerAccounts:
            accountNumber = account["accountNumber"]
            for property in properties:
                try:
                    consumers = property["consumers"]
                    propertyNumber = property["propertyNumber"]
                    timezone = get_timezone_by_sate(property["address"]["state"])
                    for consumer in consumers:
                        if consumer["accountNumber"] == accountNumber:
                            consumerNumber = consumer["consumerNumber"]
                            refresh_usage(consumerNumber, propertyNumber, timezone)
                except Exception as e:
                    logging.error(f"Failed to process account {accountNumber} for property {property['propertyNumber']}: {e}")
    except Exception as e:
        logging.critical(f"Unhandled error in main execution: {e}")

if __name__ == "__main__":
    main()
