from flask import Flask, render_template, request, redirect, session
from blockchain import Blockchain, Transaccion
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Instancia global de la blockchain
blockchain = Blockchain()

@app.route('/')
def index():
    return render_template('index.html', chain=blockchain.chain)

@app.route('/add_block', methods=['POST'])
def add_block():
    num_transacciones = int(request.form['num_transacciones'])
    session['num_transacciones'] = num_transacciones
    return redirect('/add_transactions')

@app.route('/add_transactions', methods=['GET', 'POST'])
def add_transactions():
    if request.method == 'POST':
        l_transacciones = []
        num_transacciones = session.get('num_transacciones', 0)
        
        for i in range(num_transacciones):
            pagador = request.form.get(f'transaccion_{i}_pagador')
            receptor = request.form.get(f'transaccion_{i}_receptor')
            cantidad = float(request.form.get(f'transaccion_{i}_cantidad'))
            l_transacciones.append(Transaccion(pagador, receptor, cantidad))
        
        blockchain.append_bloque(l_transacciones)
        return redirect('/')
    
    num_transacciones = session.get('num_transacciones', 0)
    return render_template('add_transactions.html', num_transacciones=num_transacciones)

if __name__ == '__main__':
    app.run(debug=True)