# Astrologico AI Features 🤖

## Overview

Astrologico v2.0 includes powerful AI-driven features for intelligent astrological interpretation, natural language querying, and advanced analysis. Powered by OpenAI GPT-4, Claude 3, or local models.

## Features

### 1. AI-Powered Interpretations
- **Chart Summaries**: Comprehensive narrative interpretations of natal charts
- **Aspect Analysis**: Intelligent explanation of planetary aspects and their meanings
- **Moon Phase Insights**: AI interpretation of lunar cycles and their influence
- **Zodiac Descriptions**: Detailed personality and life themes analysis

### 2. REST API with FastAPI
- **High-Performance Server**: Built with FastAPI for speed and reliability
- **Interactive Documentation**: Auto-generated Swagger UI at `/docs`
- **Multiple Endpoints**: Comprehensive API for all astrological functions
- **CORS Enabled**: Ready for web and mobile integrations

### 3. Natural Language Q&A
- Ask any astrological question in natural language
- Optional chart context for personalized answers
- Smart interpretation using advanced language models

### 4. Compatibility Analysis
- Two-chart compatibility assessment
- Detailed relationship dynamics
- Challenge and strength identification
- AI-powered insights on partnership potential

### 5. Transit Analysis
- Current planetary transits to natal chart
- Timing and influence predictions
- Opportunity and challenge identification
- Actionable guidance for life planning

### 6. Intelligent Caching
- Results caching to reduce API costs
- Fast repeated queries
- Configurable cache management

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure AI Provider

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```env
# Choose provider: "openai" or "anthropic"
AI_PROVIDER=openai

# OpenAI (GPT-4)
OPENAI_API_KEY=sk-your-key-here

# Anthropic (Claude)
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 3. Start the API Server

```bash
python3 api_server.py
```

Server runs at: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

## Usage Examples

### Using the Python API

```python
from astrologico import AstrologicalCalculator
from ai_interpreter import AstrologicalInterpreter
from datetime import datetime

# Initialize components
calc = AstrologicalCalculator()
interpreter = AstrologicalInterpreter(api_provider="openai")

# Generate chart with AI interpretation
dt = datetime(2000, 1, 15, 9, 30, 0)
chart = calc.generate_chart(dt=dt, lat=40.7128, lon=-74.0060)

# Get AI interpretation
summary = interpreter.generate_chart_summary(chart)
print(summary)

# Ask a question
answer = interpreter.answer_question(
    question="What does Venus in my chart mean?",
    chart_data=chart
)
print(answer)
```

### Using the REST API

#### Generate Chart with AI Interpretation

```bash
curl -X GET "http://localhost:8000/api/v1/chart/quick?date=2000-01-15T09:30:00&lat=40.7128&lon=-74.0060"
```

Response includes:
- Planetary positions
- Aspects
- Moon phase
- AI-generated summary and interpretations

#### Ask a Question

```bash
curl -X POST "http://localhost:8000/api/v1/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What does my Venus sign mean for relationships?",
    "datetime": {
      "datetime_str": "2000-01-15T09:30:00",
      "use_now": false
    },
    "location": {
      "latitude": 40.7128,
      "longitude": -74.0060
    }
  }'
```

#### Analyze Compatibility

```bash
curl -X POST "http://localhost:8000/api/v1/analysis/compatibility" \
  -H "Content-Type: application/json" \
  -d '{
    "person1_datetime": {
      "datetime_str": "2000-01-15T09:30:00",
      "use_now": false
    },
    "person1_location": {
      "latitude": 40.7128,
      "longitude": -74.0060
    },
    "person2_datetime": {
      "datetime_str": "1995-06-20T14:00:00",
      "use_now": false
    },
    "person2_location": {
      "latitude": 40.7128,
      "longitude": -74.0060
    }
  }'
```

### Using the CLI Client

```bash
# Check API status
python3 api_client.py status

# Generate chart with interpretation
python3 api_client.py chart --date "2000-01-15 09:30:00" --lat 40.7128 --lon -74.0060

# Ask questions
python3 api_client.py ask "What does Mars in Scorpio mean?" \
  --date "2000-01-15 09:30:00" \
  --lat 40.7128 \
  --lon -74.0060

# Analyze compatibility
python3 api_client.py compatibility \
  --date1 "2000-01-15" --lat1 40.7128 --lon1 -74.0060 \
  --date2 "1995-06-20" --lat2 40.7128 --lon2 -74.0060

# Get planetary positions
python3 api_client.py planets --date "2000-01-15 09:30:00" --lat 40.7128 --lon -74.0060

# Calculate aspects
python3 api_client.py aspects --date "2000-01-15 09:30:00" --orb 8.0

# Get moon phase
python3 api_client.py moon --date "2000-01-15 09:30:00"
```

## API Endpoints

### Chart Generation
- `GET /api/v1/chart/quick` - Quick chart with query parameters
- `POST /api/v1/chart/generate` - Full chart request with JSON body

### Planetary Data
- `GET /api/v1/planets` - Planetary positions
- `GET /api/v1/aspects` - Planetary aspects
- `GET /api/v1/moon` - Moon phase information

### AI Analysis
- `POST /api/v1/ask` - Natural language Q&A
- `POST /api/v1/interpret/aspects` - Aspect interpretation
- `GET /api/v1/interpret/moon` - Moon phase interpretation

### Advanced Analysis
- `POST /api/v1/analysis/compatibility` - Compatibility analysis
- `POST /api/v1/analysis/transits` - Transit analysis

### System
- `GET /api/v1/status` - API status and configuration
- `GET /health` - Health check
- `GET /` - API information

## Architecture

### ai_interpreter.py
Core module for AI-powered interpretations. Features:
- Multiple API provider support (OpenAI, Anthropic)
- Built-in caching layer
- Fallback template interpretations
- Context-aware analysis

### api_server.py
FastAPI server providing:
- RESTful endpoints for all astrological functions
- Request validation with Pydantic
- Error handling and status codes
- CORS support for web clients
- Auto-generated API documentation

### api_client.py
CLI client for API interaction:
- Simple command-line interface
- Support for all major operations
- JSON output formatting
- Connection error handling

## Cost Optimization

### Caching Strategy
The AI interpreter includes intelligent caching:
- Chart interpretations cached by content hash
- Moon phase interpretations cached for exact values
- Reuse of previous analyses reduces API costs

### Provider Recommendations
- **OpenAI**: Full features, best quality, ~$0.01-0.05 per interpretation
- **Anthropic**: Excellent quality, good price, ~$0.01-0.03 per interpretation
- **Self-hosted**: Lower cost option using local models

## Advanced Usage

### Custom Prompts

Extend the interpreter with custom prompts:

```python
from ai_interpreter import AstrologicalInterpreter

interpreter = AstrologicalInterpreter()

custom_prompt = """Analyze this astrological chart as a life coach would..."""
result = interpreter._query_ai(custom_prompt)
```

### Batch Processing

Process multiple charts efficiently:

```python
from datetime import datetime, timedelta

dates = [datetime(2000, 1, 15) + timedelta(days=i*365) for i in range(10)]

for dt in dates:
    chart = calc.generate_chart(dt=dt, lat=40.7128, lon=-74.0060)
    summary = interpreter.generate_chart_summary(chart)
    # Store or process result
```

### Integration with Web Applications

Deploy the API server:

```bash
# Using Gunicorn for production
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api_server:app --bind 0.0.0.0:8000
```

## Troubleshooting

### AI Features Not Working
1. Verify API keys in `.env` file
2. Check API provider status and quota
3. Ensure correct Python version (3.8+)
4. Test with: `python3 api_client.py status`

### API Connection Issues
1. Ensure server is running: `python3 api_server.py`
2. Check port 8000 is accessible
3. Verify firewall rules if connecting remotely

### Slow Responses
1. Enable caching (automatic)
2. Reduce orb value for aspect calculations
3. Use simpler models for faster responses
4. Consider batch operations

## Development

### Running Tests
```bash
python3 -m pytest tests/
```

### Adding New Features
1. Extend `AstrologicalInterpreter` class
2. Add new API endpoints in `api_server.py`
3. Add CLI commands to `api_client.py`

## Licensing

Same as Astrologico project.

## Support

For issues, questions, or feature requests, please refer to the main README.md and project documentation.

---

**Version**: 2.0.0  
**Last Updated**: 2026-03-29  
**Status**: Production Ready
