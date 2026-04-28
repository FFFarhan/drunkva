# DrunkVa API

🍻 Strava for drinking — track drinks and compete on leaderboards!

## Features

- 📱 User authentication with JWT tokens
- 🍺 Log drinks with predefined types
- 📊 All-time global leaderboard
- 🏆 Personal rank tracking with context
- 📈 Drink history with filtering and pagination
- ⚡ Built with FastAPI for high performance

## Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose (recommended)
- PostgreSQL 16+ (if running locally without Docker)

### Setup with Docker (Recommended)

1. **Navigate to project directory:**
   ```bash
   cd drunkva
   ```

2. **Create `.env` file:**
   ```bash
   cp .env.example .env
   ```

3. **Start services:**
   ```bash
   docker-compose up -d
   ```

   This will start:
   - PostgreSQL database on port 5432
   - FastAPI server on port 8000

4. **Verify it's running:**
   ```bash
   curl http://localhost:8000/health
   ```

5. **Access API docs:**
   Open browser to **http://localhost:8000/docs**

### Setup Locally (Without Docker)

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create `.env` file:**
   ```bash
   cp .env.example .env
   ```

4. **Update `.env` for local PostgreSQL:**
   ```
   DATABASE_URL=postgresql://drunkva:drunkva_pass@localhost:5432/drunkva_db
   ```

5. **Run server:**
   ```bash
   uvicorn app.main:app --reload
   ```

## API Endpoints

### Authentication
- `POST /auth/register` — Create new user
- `POST /auth/login` — Login with email/password

### Users
- `GET /users/me` — Get current user profile with stats
- `GET /users/{user_id}` — Get public user profile

### Drinks
- `GET /drinks/types` — List all predefined drink types
- `POST /drinks/log` — Log a drink
- `GET /drinks/my-history` — Get your drink history with pagination

### Leaderboard
- `GET /leaderboard/global` — Top 100 users by total standard drinks
- `GET /leaderboard/my-rank` — Your rank with nearby competitors

## Standard Drink Calculation

Uses NIAAA standard: **1 standard drink = 14g of pure alcohol**

Formula: `quantity_oz * (abv% / 100) / 0.0568`

### Examples:
- 12oz beer @ 5% ABV = 0.60 standard drinks
- 5oz wine @ 12% ABV = 0.60 standard drinks
- 1.5oz vodka @ 40% ABV = 0.60 standard drinks

## Database Schema

### Users Table
- `id` (int, primary key)
- `username` (string, unique)
- `email` (string, unique)
- `password_hash` (string)
- `created_at` (datetime)

### Drink Types Table
- `id` (int, primary key)
- `name` (string, unique)
- `abv_percent` (float)
- `standard_oz_per_serving` (float)

### Drinks Table
- `id` (int, primary key)
- `user_id` (foreign key → users.id)
- `drink_type_id` (foreign key → drink_types.id)
- `quantity_oz` (float)
- `standard_drinks` (decimal)
- `timestamp` (datetime)
- `party_id` (int, nullable - for future party feature)
- `notes` (string, nullable)

## Environment Variables

```env
# Database connection string
DATABASE_URL=postgresql://drunkva:drunkva_pass@db:5432/drunkva_db

# JWT secret key (change in production!)
SECRET_KEY=your-secret-key-change-in-production

# CORS allowed origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# SQL debug logging
SQL_ECHO=false
```

## API Usage Examples

### 1. Register New User

**Request:**
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "beermaster",
    "email": "user@example.com",
    "password": "secure_password_123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. Login

**Request:**
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d 'email=user@example.com&password=secure_password_123'
```

### 3. Get Drink Types

**Request:**
```bash
curl "http://localhost:8000/drinks/types"
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Beer",
    "abv_percent": 5.0,
    "standard_oz_per_serving": 12.0
  },
  {
    "id": 2,
    "name": "Wine",
    "abv_percent": 12.0,
    "standard_oz_per_serving": 5.0
  }
]
```

### 4. Log a Drink

**Request:**
```bash
curl -X POST "http://localhost:8000/drinks/log" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "drink_type_id": 1,
    "quantity_oz": 12,
    "notes": "Cold one at the bar!"
  }'
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "drink_type_id": 1,
  "quantity_oz": 12.0,
  "standard_drinks": 0.6,
  "timestamp": "2026-04-28T15:30:00",
  "notes": "Cold one at the bar!",
  "drink_type": {
    "id": 1,
    "name": "Beer",
    "abv_percent": 5.0,
    "standard_oz_per_serving": 12.0
  }
}
```

### 5. Get Your Profile

**Request:**
```bash
curl "http://localhost:8000/users/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:**
```json
{
  "id": 1,
  "username": "beermaster",
  "email": "user@example.com",
  "created_at": "2026-04-28T15:00:00",
  "total_drinks": 5.2,
  "rank": 3
}
```

### 6. Get Global Leaderboard

**Request:**
```bash
curl "http://localhost:8000/leaderboard/global?limit=10"
```

**Response:**
```json
{
  "entries": [
    {
      "rank": 1,
      "user_id": 5,
      "username": "drinker_king",
      "total_drinks": 42.5,
      "drink_count": 75,
      "last_drink_timestamp": "2026-04-28T20:15:00"
    },
    {
      "rank": 2,
      "user_id": 3,
      "username": "party_animal",
      "total_drinks": 38.2,
      "drink_count": 68,
      "last_drink_timestamp": "2026-04-28T19:45:00"
    }
  ],
  "total_users": 150
}
```

### 7. Get Your Rank

**Request:**
```bash
curl "http://localhost:8000/leaderboard/my-rank" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:**
```json
{
  "rank": 3,
  "total_drinks": 5.2,
  "drink_count": 9,
  "nearby_users": [
    {
      "rank": 1,
      "user_id": 5,
      "username": "drinker_king",
      "total_drinks": 42.5,
      "drink_count": 75,
      "last_drink_timestamp": "2026-04-28T20:15:00"
    },
    {
      "rank": 2,
      "user_id": 3,
      "username": "party_animal",
      "total_drinks": 38.2,
      "drink_count": 68,
      "last_drink_timestamp": "2026-04-28T19:45:00"
    },
    {
      "rank": 3,
      "user_id": 1,
      "username": "beermaster",
      "total_drinks": 5.2,
      "drink_count": 9,
      "last_drink_timestamp": "2026-04-28T15:30:00"
    }
  ]
}
```

## Development

### Running Tests

```bash
pytest tests/
```

### Database Migrations (Alembic)

Initialize migrations:
```bash
alembic init migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Deployment

### Deploy to AWS

1. **Build and push Docker image to ECR:**
   ```bash
   docker build -t drunkva-api .
   docker tag drunkva-api:latest <account-id>.dkr.ecr.<region>.amazonaws.com/drunkva-api:latest
   docker push <account-id>.dkr.ecr.<region>.amazonaws.com/drunkva-api:latest
   ```

2. **Deploy using ECS Fargate or AppRunner**

### Deploy to Heroku

1. **Create Heroku app:**
   ```bash
   heroku create drunkva-api
   ```

2. **Add PostgreSQL addon:**
   ```bash
   heroku addons:create heroku-postgresql:standard-0
   ```

3. **Deploy:**
   ```bash
   git push heroku main
   ```

### Deploy to DigitalOcean

1. **Build and push Docker image:**
   ```bash
   docker push your-registry/drunkva-api
   ```

2. **Deploy using App Platform or DigitalOcean Kubernetes**

## Production Checklist

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Update `DATABASE_URL` to production PostgreSQL
- [ ] Update `CORS_ORIGINS` to production domain
- [ ] Set `SQL_ECHO=false`
- [ ] Enable HTTPS
- [ ] Set up logging and monitoring
- [ ] Add rate limiting (optional)
- [ ] Set up backups for database

## Future Enhancements (Phase 2+)

- 🎉 Party/event tracking
- 🚬 Cigarette tracking & leaderboard
- 👥 Friend connections & social features
- 🏅 Achievements & badges
- 📊 Personal analytics dashboard
- 📸 Photo uploads
- ⚡ Real-time updates with WebSocket
- 📅 Weekly & monthly leaderboards
- 🔔 Push notifications

## API Documentation

Once the server is running, interactive API documentation is available at:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Support & Issues

For questions or issues, please reach out or file a GitHub issue.

## License

MIT

---

**Built with 🍻 and FastAPI**
# drunkva
