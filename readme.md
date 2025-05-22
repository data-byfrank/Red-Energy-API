# Red Energy API Data Manager

This project allows you to authenticate with the Red Energy API, fetch customer, property, and usage interval data, and store it in a local SQLite database. It is designed for automation and data analysis of your Red Energy usage. It should work for customers with multiple properties but I am not in lucky enough position to test this 😉.

## Features

- Fetches customer and property details from Red Energy.
- Downloads interval usage data for specified periods.
- Stores all data in a local SQLite database (`energy_data.db`).

## Prerequisites
- Python 3 and pip (pre-installed in the dev container)

# Getting Started

1. **Clone the repository:**
   ```sh
   git clone <repository-url>
   cd "Red Energy API"
   ```

2. **Install Python dependencies:**
   ```sh
   pip3 install -r requirements.txt
   ```
3. **Create .env file with the following info:
    - RE_USERNAME: Your Red Energy Username
    - RE_PASSWORD: Your Red Energy Password
    - RE_CLIENT_ID: You will need to use Proxyman on an IOS or Android device to capture traffic when using the red energy app to attain a client id. I am not sure if a client id has been issued for each user but its likely the client ids are generic across most mobile app installations. 
    - PRELOAD_USAGE_DAYS: Set this to the number of days you want to preload on first run. 
4. **Run main:**
   - For Python:
     ```sh
     python3 main.py
     ```

## Development

- Use the dev container for a pre-configured environment.

## Usage & Disclaimer

This work is for personal use and I am in way affiliated with Red Energy. 

**Disclaimer:**  
This project has not been fully tested and may contain bugs or unexpected behavior. Use it at your own risk. The author is not responsible for any issues, data loss, or damages that may result from using this software.

## License

This project is released into the public domain under the [Unlicense](https://unlicense.org/). You are free to use, modify, and distribute it without restriction.
