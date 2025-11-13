# AI Chatbox Setup Guide

## Quick Start

The chat widget requires two environment variables to work:

1. **GEMINI_API_KEY** — Your Google Generative AI API key
2. **GEMINI_API_URL** — The endpoint URL for Google Generative AI (REST API)

## Step 1: Get Your API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click **"Create API key"** (or copy existing key if you have one)
3. Copy the key value

## Step 2: Configure Environment Variables

### Option A: Using `.env` file (Recommended for Development)

1. Open `.env` file in project root (`c:\Users\Nguye\learning_web\mysite\.env`)
2. Replace placeholders with your actual values:

```
GEMINI_API_KEY=paste-your-api-key-here
GEMINI_API_URL=https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=paste-your-api-key-here
```

3. Save the file
4. Restart Django: `python manage.py runserver`

### Option B: Using PowerShell (Temporary, only for current session)

```powershell
$env:GEMINI_API_KEY = 'your-api-key-here'
$env:GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=your-api-key-here'
python manage.py runserver
```

## Step 3: Verify Configuration

Run the diagnostic command:

```powershell
python manage.py check_gemini
```

You should see:
- Status code: 200 (or similar 2xx)
- JSON response with model's output

If you see 404 or 401:
- **404**: URL is wrong
- **401**: API key is wrong or expired
- **429**: Rate limit exceeded

## Step 4: Test Chat Widget

1. Log in to the site (http://127.0.0.1:8000/accounts/login)
2. Go to dashboard (http://127.0.0.1:8000/accounts/user-dashboard/)
3. Click the 💬 button (floating chat widget)
4. Send a test message
5. You should receive a response from Gemini

## Troubleshooting

### Still seeing 502 error?

Run from terminal:
```powershell
python manage.py check_gemini
```

Copy the output and check:
- If it says "GEMINI_API_KEY or GEMINI_API_URL not set" → variables aren't being loaded
- If it shows 404 → endpoint URL is wrong
- If it shows 401 → API key is invalid
- If it shows connection refused → network/firewall issue

### Check if .env is loaded

```powershell
python -c "from django.conf import settings; print(settings.GEMINI_API_KEY); print(settings.GEMINI_API_URL)"
```

Both should print your actual values, not blank.

### API Key Issues

- API key must be from [Google AI Studio](https://makersuite.google.com/app/apikey)
- Make sure you copied the **entire key** (no extra spaces)
- Check that the key hasn't expired (regenerate if needed)

## Security Notes

- **NEVER commit `.env` to git** — it contains your API key
- The `.env` file is already in `.gitignore` (excluded from version control)
- For production, use environment variables from your deployment platform (AWS, Heroku, etc.)

## Model Options

You can use different Gemini models by changing the URL:

- `gemini-1.5-flash` (fast, cheaper) — recommended for chat
- `gemini-1.5-pro` (more capable, slower)
- `gemini-pro` (older model, still available)

Example for gemini-1.5-pro:
```
GEMINI_API_URL=https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key=YOUR_KEY
```
