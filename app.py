from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

# Adiciona `enumerate` ao ambiente Jinja2
app.jinja_env.globals.update(enumerate=enumerate)

# Lista de moto-taxistas com seus estados de disponibilidade
moto_taxis = [
    {'nome': 'João Silva', 'telefone': '5511999999999', 'disponivel': True, 'index': 0},
    {'nome': 'Maria Oliveira', 'telefone': '5511888888888', 'disponivel': True, 'index': 1},
    # Adicione mais moto-taxistas aqui
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/moto_taxis_disponiveis')
def moto_taxis_disponiveis():
    # Apenas moto-taxistas disponíveis
    disponiveis = [m for m in moto_taxis if m['disponivel']]
    return jsonify(disponiveis)

@app.route('/atualizar_status/<int:index>', methods=['POST'])
def atualizar_status(index):
    # Atualizar o estado de disponibilidade do moto-taxista
    moto_taxis[index]['disponivel'] = not moto_taxis[index]['disponivel']
    # Se o moto-taxista está se tornando disponível, move-o para o final da lista
    if moto_taxis[index]['disponivel']:
        moto_taxi = moto_taxis.pop(index)
        moto_taxis.append(moto_taxi)
    # Reindexa os moto-taxistas para garantir o índice correto
    for i, moto_taxi in enumerate(moto_taxis):
        moto_taxi['index'] = i
    # Emitir atualização para todos os clientes conectados
    socketio.emit('update_lista', [m for m in moto_taxis if m['disponivel']])
    return redirect(url_for('moto_taxistas'))

@app.route('/chamar_moto_taxi/<int:index>', methods=['POST'])
def chamar_moto_taxi(index):
    # Definir o moto-taxista como indisponível
    moto_taxis[index]['disponivel'] = False
    # Reindexa os moto-taxistas para garantir o índice correto
    for i, moto_taxi in enumerate(moto_taxis):
        moto_taxi['index'] = i
    # Emitir atualização para todos os clientes conectados
    socketio.emit('update_lista', [m for m in moto_taxis if m['disponivel']])
    return jsonify({'success': True})

@app.route('/moto_taxistas')
def moto_taxistas():
    # Página para os moto-taxistas atualizarem seu status
    return render_template('moto_taxistas.html', moto_taxis=moto_taxis)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0')
