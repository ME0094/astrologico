# Astrologico AI - Quick Start Guide 🚀

Get up and running with Astrologico AI features in 5 minutes.

## Option 1: Quick Local Setup

### 1. Install Dependencies
```bash
cd ~/astrologico
bash setup_ai.sh
```

### 2. Configure AI (Optional but Recommended)
```bash
# Get API keys from:
# - OpenAI: https://platform.openai.com/api-keys
# - Anthropic: https://console.anthropic.com

nano .env
# Add your API keys and save
```

### 3. Start API Server
```bash
python3 api_server.py
```

Server is now running at: **http://localhost:8000**

### 4. Test It
```bash
# In another terminal
python3 api_client.py status

# Generate a chart with AI interpretation
python3 api_client.py chart \
  --date "2000-01-15 09:30:00" \
  --lat 40.7128 \
  --lon -74.0060
```

---

## Option 2: Docker Deployment

### 1. Setup Environment
```bash
cp .env.example .env
nano .env  # Add your API keys
```

### 2. Run with Docker Compose
```bash
docker-compose up -d
```

### 3. Check Status
```bash
docker-compose logs -f astrologico-api
curl http://localhost:8000/health
```

---

## Common Tasks

### Get Full Chart with AI Interpretation
```bash
python3 api_client.py chart \
  --date "2000-01-15 09:30:00" \
  --lat 40.7128 \
  --lon -74.0060
```

### Ask an Astrological Question
```bash
python3 api_client.py ask \
  "What does Mars in Scorpio mean for my drive and passion?" \
  --date "2000-01-15 09:30:00" \
  --lat 40.7128 \
  --lon -74.0060
```

### Check Compatibility Between Two People
```bash
python3 api_client.py compatibility \
  --date1 "2000-01-15 09:30:00" --lat1 40.7128 --lon1 -74.0060 \
  --date2 "1995-06-20 14:00:00" --lat2 40.7128 --lon2 -74.0060
```

### Get Planetary Positions
```bash
python3 api_client.py planets \
  --date "2000-01-15 09:30:00" \
  --lat 40.7128 \
  --lon -74.0060
```

### Calculate Aspects
```bash
python3 api_client.py aspects \
  --date "2000-01-15 09:30:00" \
  --lat 40.7128 \
  --lon -74.0060 \
  --orb 8.0
```

### Get Moon Phase
```bash
python3 api_client.py moon --date "2000-01-15 09:30:00"
```

---

## API Interactive Documentation

Open your browser to see the full API documentation:

```
http://localhost:8000/docs
```

This gives you an interactive interface to test all API endpoints.

---

## Using the Python API Directly

```python
from datetime import datetime
from astrologico import AstrologicalCalculator
from ai_interpreter import AstrologicalInterpreter

# Initialize
calc = AstrologicalCalculator()
interpreter = AstrologicalInterpreter(api_provider="openai")

# Generate chart
dt = datetime(2000, 1, 15, 9, 30, 0)
chart = calc.generate_chart(dt=dt, lat=40.7128, lon=-74.0060)

# Get AI interpretation
summary = interpreter.generate_chart_summary(chart)
print(summary)

# Ask a question
answer = interpreter.answer_question(
    question="What does my Venus sign mean?",
    chart_data=chart
)
print(answer)
```

---

## Troubleshooting

### Server Won't Start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill process using port 8000
kill -9 <PID>

# Try again
python3 api_server.py
```

### No AI Responses
```bash
# Check your .env file
cat .env

# Verify API key is set
echo $OPENAI_API_KEY

# Test API key directly
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Check virtual environment is active
which python3  # Should show path in venv/
```

---

## Next Steps

1. Read the full AI Features documentation: [AI_FEATURES.md](AI_FEATURES.md)
2. Check the main README: [README.md](README.md)
3. Explore the interactive API docs at http://localhost:8000/docs
4. Integrate with your application using the REST API

---

## Key Resources

| Resource | Purpose |
|----------|---------|
| `AI_FEATURES.md` | Complete AI features documentation |
| `README.md` | Original Astrologico features |
| `.env.example` | Configuration template |
| `api_server.py` | REST API server |
| `api_client.py` | CLI client for API |
| `ai_interpreter.py` | AI interpretation engine |

---

**Tips:**
- 💡 Always use `--lat` and `--lon` for accurate geocentric calculations
- 🔑 Store API keys in `.env`, never use directly in code
- 🚀 Docker is recommended for production deployments
- 📊 Check `/docs` endpoint for full API reference
- ⚡ Use caching to reduce API costs

---

Have fun exploring the cosmos! 🌟
