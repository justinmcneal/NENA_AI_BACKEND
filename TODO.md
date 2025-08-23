# TODO List for NENA AI Backend

## Authentication
- **SMS Gateway Integration:** Implement actual SMS sending for OTPs using a third-party API (e.g., Twilio, Vonage). Currently, OTPs are generated but not sent via SMS.

## Test Script
- **Resend OTP Integration on Testing Script:** Implement resending of otp on testing script if in any case the user did not receive any. 

## AI-Powered Document Analyzer
What a real AI-powered document analyzer would do (and what the current setup is designed for in the future):
- **Image Preprocessing:** It would use libraries like torchvision and Pillow to prepare the image (resize, normalize, etc.).
- **Document Classification:** A trained deep learning model (like ResNet) would classify the document type (e.g., "Philippine ID Card", "Official Receipt").
- **Optical Character Recognition (OCR):** It would extract text from the image (e.g., name, address, date of birth from an ID; item names, prices, totals from a receipt).
- **Data Extraction & Validation:** It would parse the extracted text into structured data and potentially validate it against known formats or databases.
- **Authenticity Checks:** For IDs, it might perform checks for tampering or compare the photo to a selfie (if a selfie feature were implemented).