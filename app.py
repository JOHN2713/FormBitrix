from flask import Flask, render_template, request, redirect, url_for
import json
import os
from uuid import uuid4
from datetime import datetime


app = Flask(__name__)
DATA_FILE = 'data/clicks.json'

# Cargar datos o crear archivo si no existe
def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump({}, f)

    with open(DATA_FILE, 'r') as f:
        try:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
        except json.JSONDecodeError:
            return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        form_url = request.form['url']
        form_name = request.form['name']
        tracking_id = generate_short_id()
        data = load_data()
        data[tracking_id] = {
            'url': form_url,
            'name': form_name,
            'clicks': 0,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        save_data(data)
        tracking_link = request.host_url + 'track/' + tracking_id
        return render_template('index.html', tracking_link=tracking_link, form_name=form_name)
    return render_template('index.html')

@app.route('/track/<tracking_id>')
def track(tracking_id):
    data = load_data()
    if tracking_id in data:
        data[tracking_id]['clicks'] += 1
        save_data(data)
        return redirect(data[tracking_id]['url'])
    return "URL no encontrada", 404

@app.route('/dashboard')
def dashboard():
    data = load_data()
    return render_template('dashboard.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
