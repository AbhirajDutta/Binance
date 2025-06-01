from flask import Flask, request, jsonify
from data_fetcher import get_current_price
from datetime import datetime
import os
import json

app = Flask(__name__)

STATE_FILE = "state.json"

# ========== Load or Initialize State ==========
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            a = f.readlines
            print(a)
            return json.load(f)
    else:
        return {
            "position": None,
            "entry_price": 0.0,
            "quantity": 1,
            "realized_pnl": 0.0,
            "trades": []
        }

def save_state():
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

state = load_state()


@app.route('/webhook', methods=['POST'])
def webhook_receiver():
    data = request.json
    signal = data.get("signal", "").lower()
    if signal not in ["buy", "sell"]:
        return jsonify({"error": "Invalid signal"}), 400
    
    current_price = get_current_price("BTCUSDC")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    response = []

    # === BUY SIGNAL ===
    if signal == "buy":
        if state["position"] == "short":
            # Close short
            pnl = (state["entry_price"] - current_price) * state["quantity"]
            state["realized_pnl"] += pnl
            state["trades"].append({
                "time": now,
                "type": "BUY (SHORT EXIT)",
                "price": current_price,
                "pnl": pnl
            })
            response.append(f"Closed short at {current_price}, P&L: {pnl}")

        if state["position"] != "long":
            # Open long
            state["position"] = "long"
            state["entry_price"] = current_price
            state["trades"].append({
                "time": now,
                "type": "BUY (LONG ENTRY)",
                "price": current_price
            })
            response.append(f"Opened long at {current_price}")

    # === SELL SIGNAL ===
    if signal == "sell":
        if state["position"] == "long":
            # Close long
            pnl = (current_price - state["entry_price"]) * state["quantity"]
            state["realized_pnl"] += pnl
            state["trades"].append({
                "time": now,
                "type": "SELL (LONG EXIT)",
                "price": current_price,
                "pnl": pnl
            })
            response.append(f"Closed long at {current_price}, P&L: {pnl}")

        if state["position"] != "short":
            # Open short
            state["position"] = "short"
            state["entry_price"] = current_price
            state["trades"].append({
                "time": now,
                "type": "SELL (SHORT ENTRY)",
                "price": current_price
            })
            response.append(f"Opened short at {current_price}")
    save_state()

    return jsonify({
        "messages": response,
        "current_position": state["position"],
        "entry_price": state["entry_price"],
        "realized_pnl": state["realized_pnl"]
    }), 200

@app.route("/status", methods=["GET"])
def status():
    current_price = get_current_price("BTCUSDC")
    unrealized = 0.0

    if state["position"] == "long":
        unrealized = (current_price - state["entry_price"]) * state["quantity"]
    elif state["position"] == "short":
        unrealized = (state["entry_price"] - current_price) * state["quantity"]

    return jsonify({
        "symbol": "BTCUSDC",
        "current_price": current_price,
        "position": state["position"],
        "entry_price": state["entry_price"],
        "unrealized_pnl": unrealized,
        "realized_pnl": state["realized_pnl"],
        "trades": state["trades"]
    })

if __name__ == '__main__':
    app.run(debug=True)