# StayEase API Contract

Base URL: `http://localhost:8000`

---

## POST `/api/chat/{conversation_id}/message`

Send a guest message and receive the agent's reply.

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `conversation_id` | `string` | Unique session identifier (UUID recommended). Created automatically on first message. |

### Request

**Content-Type:** `application/json`

```json
{
  "message": "string (required, min length 1)"
}
```

### Response — 200 OK

```json
{
  "conversation_id": "string",
  "reply": "string",
  "intent": "search | details | book | escalate | null",
  "tool_result": "object | null",
  "needs_escalation": "boolean"
}
```

---

### Example — Property Search

**Request**
```http
POST /api/chat/conv-bd-001/message
Content-Type: application/json

{
  "message": "Cox's Bazar-এ 2 জনের জন্য 27 এপ্রিল থেকে 29 এপ্রিল পর্যন্ত রুম দরকার"
}
```

**Response — 200 OK**
```json
{
  "conversation_id": "conv-bd-001",
  "reply": "আমি Cox's Bazar-এ আপনার তারিখের জন্য 2টি সম্পত্তি পেয়েছি:\n\n1. Sea View Suite — BDT 4,500/রাত (সর্বোচ্চ 4 জন)\n2. Ocean Breeze Cottage — BDT 3,200/রাত (সর্বোচ্চ 3 জন)\n\nকোনো সম্পত্তির বিস্তারিত জানতে চাইলে বলুন।",
  "intent": "search",
  "tool_result": {
    "available": true,
    "listings": [
      {
        "id": 1,
        "title": "Sea View Suite",
        "location": "Cox's Bazar",
        "price_per_night_bdt": 4500.0,
        "max_guests": 4,
        "type": "apartment"
      },
      {
        "id": 2,
        "title": "Ocean Breeze Cottage",
        "location": "Cox's Bazar",
        "price_per_night_bdt": 3200.0,
        "max_guests": 3,
        "type": "house"
      }
    ],
    "total_found": 2
  },
  "needs_escalation": false
}
```

---

### Example — Create Booking

**Request**
```http
POST /api/chat/conv-bd-001/message
Content-Type: application/json

{
  "message": "Sea View Suite বুক করতে চাই। আমার নাম Fatema Khanam, ফোন +8801812345678"
}
```

**Response — 200 OK**
```json
{
  "conversation_id": "conv-bd-001",
  "reply": "আপনার বুকিং নিশ্চিত হয়েছে! বুকিং ID: #1001\n\nSea View Suite, Cox's Bazar\nচেক-ইন: 27 এপ্রিল 2026 | চেক-আউট: 29 এপ্রিল 2026\n2 রাত × BDT 4,500 = মোট BDT 9,000\n\nধন্যবাদ, Fatema Khanam! 🏨",
  "intent": "book",
  "tool_result": {
    "success": true,
    "booking_id": 1001,
    "total_cost_bdt": 9000.0,
    "message": "Booking confirmed for Fatema Khanam. 2 night(s) at BDT 4500.0/night. Total: BDT 9000.0."
  },
  "needs_escalation": false
}
```

---

### Example — Escalation

**Request**
```http
POST /api/chat/conv-bd-001/message
Content-Type: application/json

{
  "message": "আমার বুকিং রিফান্ড করতে চাই"
}
```

**Response — 200 OK**
```json
{
  "conversation_id": "conv-bd-001",
  "reply": "আমি দুঃখিত, আমি শুধুমাত্র আবাসন অনুসন্ধান ও বুকিং সহায়তা করতে পারি। আপনার বিষয়টি একজন মানব প্রতিনিধির কাছে পাঠানো হচ্ছে।\n\nI'm sorry, I can only help with property search and bookings. Your query is being escalated to a human agent.",
  "intent": "escalate",
  "tool_result": null,
  "needs_escalation": true
}
```

---

### Error Responses

| Status | When |
|--------|------|
| `422 Unprocessable Entity` | `message` field is missing or empty |
| `500 Internal Server Error` | Agent failure or database error |

**422 Example**
```json
{
  "detail": [
    {
      "loc": ["body", "message"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**500 Example**
```json
{
  "detail": "Agent error: Connection to Groq API timed out"
}
```

---

## GET `/api/chat/{conversation_id}/history`

Retrieve the full message history for a conversation.

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `conversation_id` | `string` | The session ID to retrieve history for |

### Response — 200 OK

```json
{
  "conversation_id": "string",
  "messages": [
    {
      "role": "user | assistant",
      "content": "string"
    }
  ],
  "needs_escalation": "boolean"
}
```

---

### Example

**Request**
```http
GET /api/chat/conv-bd-001/history
```

**Response — 200 OK**
```json
{
  "conversation_id": "conv-bd-001",
  "messages": [
    {
      "role": "user",
      "content": "Cox's Bazar-এ 2 জনের জন্য 27 এপ্রিল থেকে 29 এপ্রিল পর্যন্ত রুম দরকার"
    },
    {
      "role": "assistant",
      "content": "আমি Cox's Bazar-এ আপনার তারিখের জন্য 2টি সম্পত্তি পেয়েছি:\n\n1. Sea View Suite — BDT 4,500/রাত\n2. Ocean Breeze Cottage — BDT 3,200/রাত"
    },
    {
      "role": "user",
      "content": "Sea View Suite বুক করতে চাই। আমার নাম Fatema Khanam, ফোন +8801812345678"
    },
    {
      "role": "assistant",
      "content": "আপনার বুকিং নিশ্চিত হয়েছে! বুকিং ID: #1001 — মোট BDT 9,000"
    }
  ],
  "needs_escalation": false
}
```

---

### Error Responses

| Status | When |
|--------|------|
| `404 Not Found` | No conversation found with that ID |

**404 Example**
```json
{
  "detail": "Conversation 'conv-bd-999' not found."
}
```
