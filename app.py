"""Stock Screener Application"""
import os
from flask import Flask, render_template, jsonify
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__)

# Configuration
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', False)
PORT = int(os.getenv('PORT', 5000))


@app.route('/')
def index():
    """Home page"""
    return jsonify({
        'status': 'running',
        'app': 'Stock Screener',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/api/stock/<ticker>')
def get_stock(ticker):
    """Get stock information"""
    try:
        stock = yf.Ticker(ticker.upper())
        info = stock.info
        
        return jsonify({
            'ticker': ticker.upper(),
            'name': info.get('longName', 'N/A'),
            'price': info.get('currentPrice', 'N/A'),
            'currency': info.get('currency', 'USD'),
            'marketCap': info.get('marketCap', 'N/A'),
            'pe_ratio': info.get('trailingPE', 'N/A'),
            'dividend_yield': info.get('dividendYield', 'N/A')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=app.config['DEBUG'])
