# R2C2 Voice Coach API

FastAPI server providing REST endpoints for managing R2C2 coaching sessions and feedback data.

## Running the API Server

### Local Development

```bash
# From the server directory
cd r2c2-voice-coach/server

# Install dependencies (if not already installed)
uv sync

# Run the API server
python -m api.server

# Or with uvicorn directly
uvicorn api.server:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Environment Variables

Create a `.env` file in the server directory:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Daily.co Configuration (for WebRTC)
DAILY_DOMAIN=your-domain.daily.co
DAILY_API_KEY=your-daily-api-key

# Google API Key (for Gemini)
GOOGLE_API_KEY=your-google-api-key

# Environment
ENV=local
```

## API Endpoints

### Health Check

```
GET /health
```

Returns the health status of the API server.

### Session Management

#### Start a New Session

```
POST /api/start
Content-Type: application/json

{
  "user_id": "user123",
  "feedback_data": {
    "feedback_id": "feedback_001",
    "themes": [...],
    "raw_comments": [...]
  }
}
```

Response:
```json
{
  "session_id": 1,
  "room_url": "https://your-domain.daily.co/r2c2-session-1-...",
  "token": "your-daily-token",
  "message": "Session 1 created successfully"
}
```

#### Get Session History

```
GET /api/sessions/{user_id}
```

Returns all sessions for a specific user.

Response:
```json
{
  "user_id": "user123",
  "sessions": [
    {
      "session_id": 1,
      "user_id": "user123",
      "start_time": "2025-10-16T10:00:00",
      "end_time": "2025-10-16T10:45:00",
      "created_at": "2025-10-16T10:00:00"
    }
  ],
  "total_sessions": 1
}
```

#### Get Session Details

```
GET /api/session/{session_id}
```

Returns detailed information for a specific session including:
- Session metadata
- Feedback data
- Development plan goals
- Emotion events
- Phase transitions

#### Mark Goal as Complete

```
PUT /api/goal/{goal_id}/complete
```

Marks a development plan goal as completed.

Response:
```json
{
  "success": true,
  "goal_id": 1,
  "completed_at": "2025-10-16T11:00:00",
  "message": "Goal 1 marked as complete"
}
```

### Feedback Upload

#### Upload Feedback Data

```
POST /api/feedback/upload
Content-Type: application/json

{
  "user_id": "user123",
  "feedback_text": "Great communication skills. Could improve on delegation.",
  "feedback_file": null,
  "file_type": null
}
```

Or with a file (base64 encoded):

```json
{
  "user_id": "user123",
  "feedback_text": null,
  "feedback_file": "base64-encoded-content",
  "file_type": "csv"
}
```

Supported file types: `text`, `csv`, `json`

Response:
```json
{
  "feedback_id": "feedback_user123_20251016100000",
  "user_id": "user123",
  "parsed_themes": [
    {
      "category": "strength",
      "theme": "Communication",
      "frequency": 2,
      "examples": ["Great communication skills"]
    },
    {
      "category": "improvement",
      "theme": "Delegation",
      "frequency": 1,
      "examples": ["Could improve on delegation"]
    }
  ],
  "total_comments": 2,
  "message": "Successfully parsed 2 feedback comments into 2 themes"
}
```

## CSV Format for Feedback

Expected columns:
- `source`: Who provided the feedback (manager, peer, direct_report, self)
- `category`: Feedback category (communication, leadership, technical, etc.)
- `comment`: The actual feedback text
- `sentiment`: (optional) positive, negative, or neutral

Example:
```csv
source,category,comment,sentiment
manager,communication,Great at explaining complex ideas,positive
peer,delegation,Could delegate more tasks,negative
direct_report,leadership,Provides clear direction,positive
```

## JSON Format for Feedback

Expected structure:
```json
{
  "comments": [
    {
      "source": "manager",
      "category": "communication",
      "comment": "Great at explaining complex ideas",
      "sentiment": "positive"
    },
    {
      "source": "peer",
      "category": "delegation",
      "comment": "Could delegate more tasks",
      "sentiment": "negative"
    }
  ]
}
```

Or simplified:
```json
{
  "feedback": [
    "Great communication skills",
    "Could improve on delegation"
  ]
}
```

## Interactive API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200 OK`: Successful GET request
- `201 Created`: Successful POST request
- `400 Bad Request`: Invalid request data
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Database not initialized

Error responses include a `detail` field with a description of the error.
