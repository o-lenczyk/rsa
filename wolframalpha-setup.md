# Wolfram Alpha App ID Setup Guide

To use Wolfram Alpha support in `crack_rsa.py`, you need a Wolfram Alpha App ID. Follow these steps to obtain one:

1.  **Visit the Wolfram Alpha Developer Portal:**
    Go to [https://developer.wolframalpha.com/portal/](https://developer.wolframalpha.com/portal/)

2.  **Sign In or Create an Account:**
    If you already have a Wolfram ID, sign in. Otherwise, create a new Wolfram ID.

3.  **Register a New App ID:**
    Once logged in, navigate to the "My Apps" section (or a similar link like "Get an App ID").
    Click on "Get an App ID" or "Add an App ID".

4.  **Select the API:**
    When prompted to select an API, choose **Wolfram|Alpha API**. This is the API that provides the "Full Results API" functionality, which the `wolframalpha` Python library uses for general computational knowledge queries, including factoring. While Wolfram offers other APIs (e.g., for Wolfram Language, Wolfram Cloud), the "Wolfram|Alpha API" is the correct choice for integrating Wolfram Alpha's computational capabilities into your script for tasks like factoring.

5.  **Fill in Application Details:**
    You will be prompted to provide some details for your application.
    *   **App Name:** Choose a descriptive name (e.g., "RSA Cracker Script").
    *   **Description:** Briefly describe what your script does (e.g., "A Python script for factoring RSA moduli using various algorithms, including Wolfram Alpha.").
    *   **Usage Type:** Select "Personal Use" or "Non-Commercial Use" if applicable.

6.  **Agree to Terms of Use:**
    Read and agree to the Wolfram Alpha API Terms of Use.

7.  **Receive Your App ID:**
    After submitting, your new App ID will be displayed. It's a string of alphanumeric characters (e.g., `XXXXXX-XXXXXXXXXX`).

8.  **Update `config.py`:**
    Open the `config.py` file in your project and replace `'YOUR_WOLFRAM_ALPHA_APP_ID'` with the App ID you just obtained:

    ```python
    # config.py
    WOLFRAM_ALPHA_APP_ID = 'YOUR_ACTUAL_WOLFRAM_ALPHA_APP_ID_HERE'
    ```

    Remember not to commit your `config.py` file to public repositories if it contains your actual App ID, as it's already added to `.gitignore`.
