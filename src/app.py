from flask import Flask, render_template, request, redirect, url_for
from varasto import Varasto

app = Flask(__name__)

# In-memory storage for warehouses
varastot = {}
id_counter = [0]  # Using list to avoid global statement


def get_next_id():
    id_counter[0] += 1
    return id_counter[0]


@app.route('/')
def index():
    return render_template('index.html', varastot=varastot)


@app.route('/luo', methods=['GET', 'POST'])
def luo_varasto():
    if request.method == 'POST':
        nimi = request.form.get('nimi', 'Nimetön varasto')
        tilavuus = float(request.form.get('tilavuus', 100))
        alku_saldo = float(request.form.get('alku_saldo', 0))

        varasto_id = get_next_id()
        varastot[varasto_id] = {
            'nimi': nimi,
            'varasto': Varasto(tilavuus, alku_saldo)
        }
        return redirect(url_for('index'))

    return render_template('luo.html')


@app.route('/varasto/<int:varasto_id>')
def nayta_varasto(varasto_id):
    if varasto_id not in varastot:
        return redirect(url_for('index'))

    varasto_data = varastot[varasto_id]
    return render_template('varasto.html',
                           varasto_id=varasto_id,
                           nimi=varasto_data['nimi'],
                           varasto=varasto_data['varasto'])


@app.route('/varasto/<int:varasto_id>/muokkaa', methods=['GET', 'POST'])
def muokkaa_varasto(varasto_id):
    if varasto_id not in varastot:
        return redirect(url_for('index'))

    varasto_data = varastot[varasto_id]

    if request.method == 'POST':
        nimi = request.form.get('nimi', varasto_data['nimi'])
        varasto_data['nimi'] = nimi
        return redirect(url_for('nayta_varasto', varasto_id=varasto_id))

    return render_template('muokkaa.html',
                           varasto_id=varasto_id,
                           nimi=varasto_data['nimi'],
                           varasto=varasto_data['varasto'])


@app.route('/varasto/<int:varasto_id>/lisaa', methods=['POST'])
def lisaa_varastoon(varasto_id):
    if varasto_id not in varastot:
        return redirect(url_for('index'))

    maara = float(request.form.get('maara', 0))
    varastot[varasto_id]['varasto'].lisaa_varastoon(maara)
    return redirect(url_for('nayta_varasto', varasto_id=varasto_id))


@app.route('/varasto/<int:varasto_id>/ota', methods=['POST'])
def ota_varastosta(varasto_id):
    if varasto_id not in varastot:
        return redirect(url_for('index'))

    maara = float(request.form.get('maara', 0))
    varastot[varasto_id]['varasto'].ota_varastosta(maara)
    return redirect(url_for('nayta_varasto', varasto_id=varasto_id))


@app.route('/varasto/<int:varasto_id>/poista', methods=['POST'])
def poista_varasto(varasto_id):
    if varasto_id in varastot:
        del varastot[varasto_id]
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
