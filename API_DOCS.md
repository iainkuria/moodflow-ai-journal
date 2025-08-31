# MoodFlow API Documentation 📚

## Base URL
```
Development: http://localhost:5000
Production: https://your-deployed-app.com
```

## Authentication
No authentication required for public endpoints. API keys are handled server-side.

---

## Endpoints

### 1. Create Journal Entry
**POST** `/api/entry`

Creates a new journal entry and analyzes sentiment.

**Request Body:**
```json
{
    "text": "I had an amazing day today! Everything went perfectly."
}
```

**Response (201 Created):**
```json
{
    "id": 1,
    "content": "I had an amazing day today! Everything went perfectly.",
    "date_created": "2025-08-31T14:30:00.000000",
    "sentiment_label": "POSITIVE",
    "sentiment_score": 0.8945,
    "premium_unlocked": false,
    "premium_analysis": null
}
```

**Error Response (400 Bad Request):**
```json
{
    "error": "Text is required"
}
```

---

### 2. Get All Entries
**GET** `/api/entries`

Retrieves all journal entries, ordered by creation date (newest first).

**Response (200 OK):**
```json
[
    {
        "id": 2,
        "content": "Today was challenging...",
        "date_created": "2025-08-31T16:45:00.000000",
        "sentiment_label": "NEGATIVE",
        "sentiment_score": 0.7234,
        "premium_unlocked": true,
        "premium_analysis": "It sounds like you're going through a tough time..."
    },
    {
        "id": 1,
        "content": "I had an amazing day today!",
        "date_created": "2025-08-31T14:30:00.000000",
        "sentiment_label": "POSITIVE", 
        "sentiment_score": 0.8945,
        "premium_unlocked": false,
        "premium_analysis": null
    }
]
```

---

### 3. Create Payment Link
**POST** `/api/create-payment-link`

Creates an IntaSend payment link for unlocking premium insights.

**Request Body:**
```json
{
    "entry_id": 1
}
```

**Response (200 OK):**
```json
{
    "payment_url": "https://sandbox.intasend.com/pay/invoice/12345-abcdef"
}
```

**Error Response (400 Bad Request):**
```json
{
    "error": "Entry ID is required"
}
```

**Error Response (500 Internal Server Error):**
```json
{
    "error": "Payment service unavailable"
}
```

---

### 4. Payment Webhook
**POST** `/api/payment-webhook`

**⚠️ Internal endpoint** - Called by IntaSend after successful payments.

**Headers Required:**
```
X-IntaSend-Signature: webhook_signature_hash
Content-Type: application/json
```

**Request Body (from IntaSend):**
```json
{
    "state": "COMPLETE",
    "reference": "moodflow_insight_1",
    "metadata": {
        "entry_id": "1",
        "product": "premium_insight"
    },
    "amount": 50,
    "currency": "KES"
}
```

**Response (200 OK):**
```json
{
    "status": "success"
}
```

**Error Response (401 Unauthorized):**
```json
{
    "error": "Invalid signature"
}
```

---

### 5. Generate AI Insight
**POST** `/api/generate-insight`

Generates personalized AI insight for a premium-unlocked entry.

**Request Body:**
```json
{
    "entry_id": 1
}
```

**Response (200 OK):**
```json
{
    "insight": "It sounds like you had a wonderful day! This positive energy is something to cherish and build upon. Consider what specific elements made your day so special - was it accomplishing goals, connecting with others, or perhaps taking care of yourself? Recognizing these patterns can help you recreate more days like this. Your optimism shines through your words, and that's a powerful foundation for continued well-being."
}
```

**Error Response (402 Payment Required):**
```json
{
    "error": "Premium not unlocked for this entry"
}
```

**Error Response (404 Not Found):**
```json
{
    "error": "Entry not found"
}
```

---

### 6. Health Check
**GET** `/health`

Simple health check endpoint for monitoring.

**Response (200 OK):**
```json
{
    "status": "healthy",
    "timestamp": "2025-08-31T16:45:00.123456"
}
```

---

## Data Models

### JournalEntry
```python
{
    "id": int,                    # Primary key
    "content": str,               # Journal entry text
    "date_created": datetime,     # UTC timestamp
    "sentiment_label": str,       # "POSITIVE", "NEGATIVE", "NEUTRAL"
    "sentiment_score": float,     # Confidence score (0.0 - 1.0)
    "premium_unlocked": bool,     # Payment status
    "premium_analysis": str|null  # AI-generated insight
}
```

---

## Error Handling

### HTTP Status Codes
- **200** - Success
- **201** - Created (new journal entry)
- **400** - Bad Request (missing/invalid data)
- **401** - Unauthorized (invalid webhook signature)
- **402** - Payment Required (premium not unlocked)
- **404** - Not Found (entry doesn't exist)
- **500** - Internal Server Error (service unavailable)

### Error Response Format
```json
{
    "error": "Human-readable error message"
}
```

---

## Integration Examples

### Frontend JavaScript
```javascript
// Create journal entry
async function createEntry(text) {
    const response = await fetch('/api/entry', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
    });
    return await response.json();
}

// Create payment
async function createPayment(entryId) {
    const response = await fetch('/api/create-payment-link', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ entry_id: entryId })
    });
    const data = await response.json();
    window.location.href = data.payment_url;
}
```

### Python Client
```python
import requests

# Create entry
response = requests.post('http://localhost:5000/api/entry', 
                        json={'text': 'I feel great today!'})
entry = response.json()

# Get all entries
response = requests.get('http://localhost:5000/api/entries')
entries = response.json()
```

---

## Rate Limits

### Current Limits (Development)
- No rate limiting implemented
- Consider implementing in production:
  - 100 requests/hour per IP
  - 10 journal entries/day per user
  - 5 payment attempts/hour per user

### External API Limits
- **Hugging Face**: 1000 requests/month (free tier)
- **OpenAI**: $5 free credit for new accounts
- **IntaSend**: No limits on sandbox, 2.5% fee on production

---

## Webhook Security

### Signature Verification
```python
import hmac
import hashlib

def verify_intasend_signature(payload, signature, secret):
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected_signature)
```

### Testing Webhooks Locally
```bash
# Install ngrok for local webhook testing
ngrok http 5000

# Update IntaSend callback URL to:
# https://your-ngrok-url.ngrok.io/api/payment-webhook
```

---

## Database Schema

### SQLite Schema
```sql
CREATE TABLE journal_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    sentiment_label VARCHAR(20),
    sentiment_score FLOAT,
    premium_unlocked BOOLEAN DEFAULT FALSE,
    premium_analysis TEXT
);
```

### Indexes for Performance
```sql
CREATE INDEX idx_date_created ON journal_entries(date_created DESC);
CREATE INDEX idx_premium_unlocked ON journal_entries(premium_unlocked);
```

---

## Monitoring & Analytics

### Key Metrics to Track
- **User Engagement**: Entries per user per week
- **Conversion Rate**: Free → Premium insight purchases
- **Revenue**: Daily/monthly revenue from insights
- **AI Performance**: Sentiment analysis accuracy feedback
- **Payment Success**: IntaSend transaction completion rates

### Recommended Tools
- **Application Monitoring**: Sentry for error tracking
- **Analytics**: Google Analytics 4 for user behavior
- **Uptime**: UptimeRobot for service monitoring
- **Logs**: Papertrail or Loggly for centralized logging