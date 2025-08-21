# NENA AI: Nurturing Entrepreneurs, Nurturing Access

## Project Overview

### Problem Statement
BPI has established itself as a pioneer in financial inclusion through its microfinance arm, BanKo, and its flagship NegosyoKo loan programs, designed to empower MSMEs and self-employed microentrepreneurs (SEMEs). However, a significant portion of the Filipino population—particularly those in the likes of vendors, market sellers, and sari-sari store owners—remain underbanked or completely financially excluded.

For individuals whose business is unregistered and whose only financing option is often informal and exploitative, the challenge is not just financial access, but understanding, trust, and empowerment.

The gap isn't due to a lack of offerings—it’s the delivery model. Traditional microfinance outreach is human-heavy, time-consuming, and difficult to scale to the tens of thousands of entrepreneurs in need. Many of them fear or misunderstand formal lending processes, and lack the digital or financial literacy needed to engage with conventional systems.

To continue alleviating poverty and empowering underserved populations, BPI must enhance its reach through scalable, empathetic, and intelligent tools—ones that extend human impact, not replace it.

### Solution Description
To further BPI’s mission of financial inclusion and sustainable business growth, we propose the NENA AI — a mobile platform developed specifically for Android that autonomously guides and qualifies underbanked entrepreneurs toward formal financial services, with an integrated web application designed for use by loan officers. This intelligent solution acts as a personalized financial bridge between BPI and vendors, who represent the unregistered and underserved segments of the Philippine economy.

Many unbanked microentrepreneurs do not understand how loans work or fear hidden charges, making them more likely to rely on predatory lenders. The NENA AI addresses this gap not just by providing access, but by building financial confidence through personalized loan education in local languages.

**How it works:**
1.  **Filipino (and Dialect-Capable) AI Financial Assistant:** Users interact with an AI agent that explains BPI loan products step-by-step, explains terms like interest, repayment, and loans in Filipino or Pangasinan, and handles FAQs.
2.  **Personalized Loan Education Engine:** Based on the user’s background, the AI delivers custom guidance, helping users understand which loans they qualify for and how to repay them responsibly.
3.  **AI-Powered Document Analyzer (CNN):** Uses image recognition to verify receipts, IDs, and documents, helping pre-screen users.
4.  **Alternative Data Profiler:** Builds financial profiles using indicators like business habits, lifestyle, and education level.
5.  **Vendor & BPI Analytics Dashboards:** Offers basic visual business tracking for users and provides heatmaps and insight reports for BPI.
6.  **Kiosk-Ready Interface for Low-Tech Users:** Deployable in barangay centers, public markets, or with BPI field officers.
7.  **Cross-Platform Deployment:** Android mobile platform for entrepreneurs and an integrated web application for loan officers.

## Technology Stack

*   **Backend:** Python (Django, Django REST Framework)
*   **AI/ML:** FAISS, Mistral, LangChain, Llama Model, ResNet18, PyTorch
*   **Mobile:** Kotlin (for Android)

## Setup and Installation

Follow these steps to set up the NENA AI Backend locally:

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd NENA_AI_BACKEND
    ```

2.  **Create and activate a Python virtual environment:**
    It's highly recommended to use a virtual environment to manage project dependencies.
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run database migrations:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5.  **Run the development server:**
    ```bash
    python manage.py runserver 0.0.0.0:8000
    ```

    The API will be accessible at `http://127.0.0.1:8000/`.

### Testing the API

To test the user authentication flow, you can use the provided Python script:

1.  **Ensure the Django development server is running** (as per step 5 above).
2.  **Run the test script** in a new terminal (make sure your virtual environment is activated):
    ```bash
    python scripts/test_users_auth.py
    ```
3.  **Follow the prompts:** The script will ask you to enter the OTP, which will be printed in your Django server's console.

## Project Structure

*   **`nena_ai_backend/`**: The main Django project folder.
    *   `settings.py`: Configured with the new apps and Django Rest Framework.
    *   `urls.py`: Configured to route API requests to the appropriate apps.
*   **`users/`**: App for user management and authentication.
*   **`loans/`**: App for handling loan products and applications.
*   **`documents/`**: App for managing document uploads and analysis.
*   **`chat/`**: App for the AI-powered financial assistant.
*   **`analytics/`**: App for providing data to the dashboards.

