# Item Search Notifier

A web application that allows users to search for specific items and receive SMS notifications when matches are found.

## Features

- User registration and authentication
- Create and manage item search requests
- Daily automated searches using Gemini 2.5 Pro
- SMS notifications when matches are found
- Web interface to manage search requests

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with the following variables:
   ```
   DATABASE_URL=sqlite:///./search.db
   GOOGLE_API_KEY=your_gemini_api_key
   TWILIO_ACCOUNT_SID=your_twilio_sid
   TWILIO_AUTH_TOKEN=your_twilio_token
   TWILIO_PHONE_NUMBER=your_twilio_phone
   SECRET_KEY=your_secret_key
   ```
5. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## Environment Variables

- `DATABASE_URL`: Database connection string
- `GOOGLE_API_KEY`: Gemini API key
- `TWILIO_ACCOUNT_SID`: Twilio account SID
- `TWILIO_AUTH_TOKEN`: Twilio auth token
- `TWILIO_PHONE_NUMBER`: Twilio phone number for sending SMS
- `SECRET_KEY`: Secret key for JWT token generation

## API Documentation

Once the application is running, visit `/docs` for the interactive API documentation. 