from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from uuid import uuid4
from datetime import datetime
import random
import string
from flask import Response
import csv

app = Flask(__name__)
# Configuración de la base de datos SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///form_links.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo
class FormLink(db.Model):
    __tablename__ = 'form_link'
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    clicks = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Crear tablas automáticamente
with app.app_context():
    db.create_all()

# Función para generar ID corto
def generate_short_id(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        form_name = request.form['name']
        form_url = request.form['url']
        tracking_id = generate_short_id()

        # Crear nuevo registro
        new_link = FormLink(id=tracking_id, name=form_name, url=form_url)
        db.session.add(new_link)
        db.session.commit()

        tracking_link = request.host_url + 'track/' + tracking_id
        return render_template('index.html', tracking_link=tracking_link, form_name=form_name)
    return render_template('index.html')

@app.route('/track/<tracking_id>')
def track(tracking_id):
    link = FormLink.query.get_or_404(tracking_id)
    link.clicks += 1
    db.session.commit()
    return redirect(link.url)


@app.route('/dashboard')
def dashboard():
    links = FormLink.query.order_by(FormLink.created_at.desc()).all()
    return render_template('dashboard.html', links=links)

@app.route('/edit/<tracking_id>', methods=['GET', 'POST'])
def edit(tracking_id):
    link = FormLink.query.get_or_404(tracking_id)
    if request.method == 'POST':
        link.name = request.form['name']
        link.url = request.form['url']
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('edit.html', link=link)

@app.route('/delete/<tracking_id>', methods=['POST'])
def delete(tracking_id):
    link = FormLink.query.get_or_404(tracking_id)
    db.session.delete(link)
    db.session.commit()
    return redirect(url_for('dashboard'))


@app.route('/export')
def export():
    links = FormLink.query.all()
    output = []
    output.append(['ID', 'Nombre', 'URL', 'Clics', 'Fecha de Creación'])
    for link in links:
        output.append([
            link.id,
            link.name,
            link.url,
            link.clicks,
            link.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])

    # Crear archivo CSV en memoria
    si = "\n".join([",".join(map(str, row)) for row in output])
    return Response(si, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=form_links.csv"})


if __name__ == '__main__':
    is_render = 'RENDER' in os.environ  # Render agrega esta variable automáticamente
    port = int(os.environ.get('PORT', 5000))
    app.run(
        host='0.0.0.0' if is_render else '127.0.0.1',
        port=port,
        debug=not is_render
    )
