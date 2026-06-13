from flask import Flask, request, jsonify
import anthropic
import os
from binance.client import Client

app = Flask(__name__)

claude = anthropic.Anthropic(api_key=os.environ.get("CLAUDE_API_KEY"))
binance = Client(os.environ.get("BINANCE_API_KEY"), os.environ.get("BINANCE_SECRET_KEY"))

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    symbol = data.get('symbol', 'BTCUSDT')
    signal = data.get('signal', '')
    price = data.get('price', '')

    message = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=200,
        messages=[{
            "role": "user",
            "content": f"Trading signal: {signal} for {symbol} at price {price}. Should I execute this trade? Reply with only BUY, SELL, or SKIP and a brief reason."
        }]
    )

    decision = message.content[0].text
    print(f"Claude says: {decision}")

    if "BUY" in decision.upper():
        order = binance.order_market_buy(symbol=symbol, quoteOrderQty=10)
        return jsonify({"action": "BUY", "order": str(order), "claude": decision})
    elif "SELL" in decision.upper():
        order = binance.order_market_sell(symbol=symbol, quoteOrderQty=10)
        return jsonify({"action": "SELL", "order": str(order), "claude": decision})
    else:
        return jsonify({"action": "SKIP", "claude": decision})

@app.route('/')
def home():
    return "Bot is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
