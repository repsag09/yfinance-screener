# Stock Screener

A powerful stock screener application using Yahoo Finance data and Alpaca Markets API integration.

## Features

- 📊 Real-time stock data from Yahoo Finance
- 🚀 Alpaca Markets integration for trading
- 📈 Advanced technical analysis
- 🌐 RESTful API endpoints
- 🐳 Docker & Railway.app ready

## Prerequisites

- Python 3.11+
- pip or poetry
- Railway.app account (for deployment)

## Installation

### Local Development

```bash
# Clone the repository
git clone https://github.com/repsag09/yfinance-screener.git
cd yfinance-screener

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

## Deployment

### Railway.app

1. Install Railway CLI:
   ```bash
   npm i -g @railway/cli
   ```

2. Login to Railway:
   ```bash
   railway login
   ```

3. Link your project:
   ```bash
   railway link
   ```

4. Deploy:
   ```bash
   railway up
   ```

### Environment Variables

Set these on Railway.app or locally in `.env`:

```bash
FLASK_DEBUG=False
PORT=5000
ALPACA_API_KEY=your_key_here
ALPACA_SECRET_KEY=your_secret_here
```

## API Endpoints

### Health Check
```
GET /health
```

### Get Stock Info
```
GET /api/stock/{ticker}
```

Example:
```bash
curl https://your-railway-app.up.railway.app/api/stock/AAPL
```

## Dependencies

- **yfinance** - Yahoo Finance data
- **pandas** - Data manipulation
- **numpy** - Numerical computing
- **alpaca-trade-api** - Alpaca Markets integration
- **flask** - Web framework
- **gunicorn** - Production server
- **requests** - HTTP library
- **beautifulsoup4** - Web scraping

## Project Structure

```
.
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Procfile              # Heroku/Railway process definitions
├── runtime.txt           # Python version specification
├── railway.json          # Railway.app configuration
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please open an issue on GitHub.

---

**Status**: Production Ready ✨
