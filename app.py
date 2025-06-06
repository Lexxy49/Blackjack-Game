from flask import Flask, jsonify, request, session, send_from_directory
from flask_cors import CORS
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key in production
CORS(app)

# -----------------------------
# Card, Deck, and Hand Classes
# -----------------------------

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank  # Dict with 'rank' and 'value'

    def to_dict(self):
        return {
            "suit": self.suit,
            "rank": self.rank["rank"],
            "value": self.rank["value"]
        }

class Deck:
    def __init__(self):
        suits = ["spades", "clubs", "hearts", "diamonds"]
        ranks = [
            {"rank": "A", "value": 11},
            {"rank": "2", "value": 2},
            {"rank": "3", "value": 3},
            {"rank": "4", "value": 4},
            {"rank": "5", "value": 5},
            {"rank": "6", "value": 6},
            {"rank": "7", "value": 7},
            {"rank": "8", "value": 8},
            {"rank": "9", "value": 9},
            {"rank": "10", "value": 10},
            {"rank": "J", "value": 10},
            {"rank": "Q", "value": 10},
            {"rank": "K", "value": 10}
        ]
        self.cards = [Card(suit, rank) for suit in suits for rank in ranks]
        random.shuffle(self.cards)

    def deal(self, num):
        return [self.cards.pop() for _ in range(num)]

class Hand:
    def __init__(self, dealer=False):
        self.cards = []
        self.dealer = dealer

    def add_card(self, new_cards):
        self.cards.extend(new_cards)

    def calculate_value(self):
        total = 0
        aces = 0
        for card in self.cards:
            total += card.rank["value"]
            if card.rank["rank"] == "A":
                aces += 1
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    def to_dict(self, reveal=False):
        if self.dealer and not reveal:
            return [{"hidden": True}] + [card.to_dict() for card in self.cards[1:]]
        return [card.to_dict() for card in self.cards]

# -----------------------
# Game API Endpoints
# -----------------------

@app.route('/start', methods=['POST'])
def start_game():
    session['games_played'] = session.get('games_played', 0) + 1

    deck = Deck()
    player_hand = Hand()
    dealer_hand = Hand(dealer=True)

    player_hand.add_card(deck.deal(2))
    dealer_hand.add_card(deck.deal(2))

    session['deck'] = [card.to_dict() for card in deck.cards]
    session['player'] = [card.to_dict() for card in player_hand.cards]
    session['dealer'] = [card.to_dict() for card in dealer_hand.cards]

    return jsonify({
        "player": player_hand.to_dict(),
        "dealer": dealer_hand.to_dict(),
        "games_played": session['games_played']
    })

@app.route('/hit', methods=['POST'])
def hit():
    deck = Deck()
    deck.cards = [Card(c['suit'], {"rank": c['rank'], "value": c['value']}) for c in session['deck']]
    player_hand = Hand()
    player_hand.cards = [Card(c['suit'], {"rank": c['rank'], "value": c['value']}) for c in session['player']]

    new_card = deck.deal(1)
    player_hand.add_card(new_card)

    session['deck'] = [card.to_dict() for card in deck.cards]
    session['player'] = [card.to_dict() for card in player_hand.cards]

    value = player_hand.calculate_value()

    return jsonify({
        "player": player_hand.to_dict(),
        "value": value,
        "bust": value > 21
    })

@app.route('/stand', methods=['POST'])
def stand():
    deck = Deck()
    deck.cards = [Card(c['suit'], {"rank": c['rank'], "value": c['value']}) for c in session['deck']]
    dealer_hand = Hand(dealer=True)
    dealer_hand.cards = [Card(c['suit'], {"rank": c['rank'], "value": c['value']}) for c in session['dealer']]
    player_cards = [Card(c['suit'], {"rank": c['rank'], "value": c['value']}) for c in session['player']]
    player_hand = Hand()
    player_hand.cards = player_cards

    while dealer_hand.calculate_value() < 17:
        dealer_hand.add_card(deck.deal(1))

    player_value = player_hand.calculate_value()
    dealer_value = dealer_hand.calculate_value()

    if dealer_value > 21 or player_value > dealer_value:
        result = "You win!"
    elif player_value < dealer_value:
        result = "Dealer wins!"
    else:
        result = "Tie!"

    return jsonify({
        "dealer": dealer_hand.to_dict(reveal=True),
        "value": dealer_value,
        "result": result
    })

# -----------------------
# Static File Routes
# -----------------------

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

# -----------------------
# Run the App
# -----------------------

if __name__ == '__main__':
    app.run(debug=True)
