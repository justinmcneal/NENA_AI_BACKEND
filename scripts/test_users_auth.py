import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/users/"

def register_user(phone_number):
    print(f"\n--- Registering user {phone_number} ---")
    url = BASE_URL + "register/"
    data = {"phone_number": phone_number}
    response = requests.post(url, json=data)
    print("Status Code:", response.status_code)
    print("Response:", response.json())
    return response.json()

def verify_otp(phone_number, otp_code):
    print(f"\n--- Verifying OTP {otp_code} for {phone_number} ---")
    url = BASE_URL + "verify-otp/"
    data = {"phone_number": phone_number, "otp_code": otp_code}
    response = requests.post(url, json=data)
    print("Status Code:", response.status_code)
    print("Response:", response.json())
    return response.json()

def complete_profile(access_token, first_name, middle_name, last_name):
    print(f"\n--- Completing profile for {first_name} {last_name} ---")
    url = BASE_URL + "complete-profile/"
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "first_name": first_name,
        "middle_name": middle_name,
        "last_name": last_name
    }
    response = requests.post(url, headers=headers, json=data)
    print("Status Code:", response.status_code)
    print("Response:", response.json())
    return response.json()

def set_pin(access_token, phone_number, pin):
    print(f"\n--- Setting PIN for {phone_number} ---")
    url = BASE_URL + "set-pin/"
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {"phone_number": phone_number, "pin": pin}
    response = requests.post(url, headers=headers, json=data)
    print("Status Code:", response.status_code)
    print("Response:", response.json())
    return response.json()

def login_with_pin(phone_number, pin):
    print(f"\n--- Logging in with PIN for {phone_number} ---")
    url = BASE_URL + "login-with-pin/"
    data = {"phone_number": phone_number, "pin": pin}
    response = requests.post(url, json=data)
    print("Status Code:", response.status_code)
    print("Response:", response.json())
    return response.json()

def resend_otp(phone_number):
    print(f"\n--- Resending OTP for {phone_number} ---")
    url = BASE_URL + "resend-otp/"
    data = {"phone_number": phone_number}
    response = requests.post(url, json=data)
    print("Status Code:", response.status_code)
    print("Response:", response.json())
    return response

if __name__ == "__main__":
    # IMPORTANT: Replace with a unique phone number for each test run
    # The OTP will be printed in your Django server console.
    test_phone_number = "+639171234567" # Change this for each test
    test_pin = "1234"

    # Step 1: Register User
    register_response = register_user(test_phone_number)
    if register_response and register_response.get("message") == "OTP sent successfully.":
        print("\n*** Check your Django server console for the OTP ***")
        otp_code = input("Enter the OTP from the Django console: ")

        # Step 2: Verify OTP
        verify_response = verify_otp(test_phone_number, otp_code)
        if verify_response and verify_response.get("access"):
            access_token = verify_response["access"]
            refresh_token = verify_response["refresh"]
            print(f"Access Token: {access_token}")
            print(f"Refresh Token: {refresh_token}")

            # Step 3: Complete Profile
            complete_profile_response = complete_profile(access_token, "John", "M.", "Doe")

            # Step 4: Set PIN
            set_pin_response = set_pin(access_token, test_phone_number, test_pin)

            # Step 5: Login with PIN
            login_response = login_with_pin(test_phone_number, test_pin)

            # Test with wrong PIN
            print("\n--- Testing login with wrong PIN ---")
            login_with_pin(test_phone_number, "0000")

            # Test with non-existent phone number
            print("\n--- Testing login with non-existent phone number ---")
            login_with_pin("+639999999999", "1234")

            # Test Resend OTP (should succeed)
            print("\n--- Testing Resend OTP (should succeed) ---")
            resend_otp(test_phone_number)

            # Test Resend OTP again immediately (should fail due to 5-min limit)
            print("\n--- Testing Resend OTP again immediately (should fail) ---")
            resend_otp(test_phone_number)

        else:
            print("OTP verification failed.")
    else:
        print("User registration failed.")
