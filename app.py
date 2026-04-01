from flask import Flask, render_template, jsonify, request
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

# 台灣證交所 API
TWSE_API_BASE = "https://www.twse.com.tw/exchangeReport"

def get_stock_price(stock_code, date=None):
    """從台灣證交所獲取股票數據"""
    try:
        if date is None:
            date = datetime.now().strftime('%Y%m%d')
        else:
            date = datetime.strptime(date, '%Y-%m-%d').strftime('%Y%m%d')
        
        url = f"{TWSE_API_BASE}/STOCK_DAY"
        params = {
            'response': 'json',
            'date': date,
            'stockNo': stock_code
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        data = response.json()
        return data
    except Exception as e:
        return {'error': str(e)}

@app.route('/')
def index():
    """主頁面"""
    return render_template('index.html')

@app.route('/api/price/<stock_code>', methods=['GET'])
def api_price(stock_code):
    """API：獲取最新股價"""
    data = get_stock_price(stock_code)
    
    if 'data' in data and data['data']: 
        latest = data['data'][-1]
        return jsonify({
            'stock_code': stock_code,
            'date': latest[0],
            'open': float(latest[1]),
            'high': float(latest[2]),
            'low': float(latest[3]),
            'close': float(latest[4]),
            'volume': int(latest[6])
        })
    
    return jsonify({'error': '找不到股票數據'}), 404

@app.route('/api/history/<stock_code>', methods=['GET'])
def api_history(stock_code):
    """API：獲取股票歷史數據"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    try:
        if end_date is None:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        if start_date is None:
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        
        all_data = []
        current_date = start_date
        
        while current_date <= end_date:
            if current_date.weekday() < 5:
                data = get_stock_price(stock_code, current_date.strftime('%Y-%m-%d'))
                if 'data' in data and data['data']:
                    all_data.extend(data['data'])
            current_date += timedelta(days=1)
        
        return jsonify({'data': all_data, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
