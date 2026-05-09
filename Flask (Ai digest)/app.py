import json
import os
from flask import Flask, render_template, jsonify

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__,
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))

def load_cards():
    with open(os.path.join(BASE_DIR, 'content.json'), 'r', encoding='utf-8') as f:
        return json.load(f)

@app.route('/')
def index():
    data = load_cards()
    # Собираем все уникальные теги для фильтра
    all_tags = set()
    for card in data['cards']:
        all_tags.update(card['tags'])
    return render_template('index.html', cards=data['cards'], tags=sorted(all_tags))

@app.route('/api/cards')
def api_cards():
    data = load_cards()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)