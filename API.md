# Pokémon Smile API Documentation

This document provides detailed information about the API endpoints available in the Pokémon Smile application.

## Authentication Endpoints

### POST /api/auth/register
Register a new user account.

**Request Body:**
```json
{
    "username": "string",
    "password": "string",
    "email": "string"
}
```

**Response:**
```json
{
    "success": true,
    "message": "User registered successfully",
    "user_id": "string"
}
```

### POST /api/auth/login
Login to an existing account.

**Request Body:**
```json
{
    "username": "string",
    "password": "string"
}
```

**Response:**
```json
{
    "success": true,
    "token": "string",
    "user": {
        "id": "string",
        "username": "string",
        "pokemon_count": number
    }
}
```

## User Profile Endpoints

### GET /api/profile
Get the current user's profile information.

**Headers:**
- Authorization: Bearer {token}

**Response:**
```json
{
    "username": "string",
    "email": "string",
    "pokemon_count": number,
    "join_date": "string",
    "buddy_pokemon": {
        "id": number,
        "name": "string",
        "sprite_url": "string"
    }
}
```

### PUT /api/profile
Update user profile information.

**Headers:**
- Authorization: Bearer {token}

**Request Body:**
```json
{
    "email": "string",
    "buddy_pokemon_id": number
}
```

**Response:**
```json
{
    "success": true,
    "message": "Profile updated successfully"
}
```

## Pokémon Endpoints

### GET /api/pokemon
Get user's caught Pokémon collection.

**Headers:**
- Authorization: Bearer {token}

**Query Parameters:**
- page (optional): Page number for pagination
- limit (optional): Number of items per page

**Response:**
```json
{
    "pokemon": [
        {
            "id": number,
            "name": "string",
            "sprite_url": "string",
            "catch_date": "string"
        }
    ],
    "total_count": number,
    "page": number,
    "total_pages": number
}
```

### POST /api/pokemon/catch
Record a caught Pokémon after successful brushing session.

**Headers:**
- Authorization: Bearer {token}

**Request Body:**
```json
{
    "session_id": "string",
    "brushing_score": number
}
```

**Response:**
```json
{
    "success": true,
    "pokemon": {
        "id": number,
        "name": "string",
        "sprite_url": "string"
    },
    "message": "You caught a {pokemon_name}!"
}
```

## Brushing Session Endpoints

### POST /api/session/start
Start a new brushing session.

**Headers:**
- Authorization: Bearer {token}

**Response:**
```json
{
    "session_id": "string",
    "start_time": "string",
    "shadow_pokemon": {
        "silhouette_url": "string"
    }
}
```

### POST /api/session/{session_id}/complete
Complete a brushing session.

**Headers:**
- Authorization: Bearer {token}

**Request Body:**
```json
{
    "duration": number,
    "motion_score": number,
    "coverage_score": number
}
```

**Response:**
```json
{
    "success": true,
    "total_score": number,
    "achievements": ["string"],
    "next_milestone": number
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
    "error": "string",
    "message": "Detailed error message"
}
```

### 401 Unauthorized
```json
{
    "error": "unauthorized",
    "message": "Invalid or expired token"
}
```

### 404 Not Found
```json
{
    "error": "not_found",
    "message": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
    "error": "server_error",
    "message": "An unexpected error occurred"
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse:
- 100 requests per minute per IP address
- 1000 requests per hour per user token

Rate limit headers are included in all responses:
- X-RateLimit-Limit: Maximum requests allowed in the current time window
- X-RateLimit-Remaining: Number of requests remaining in the current window
- X-RateLimit-Reset: Time when the current window resets (Unix timestamp) 