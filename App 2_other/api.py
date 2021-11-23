from flask import Flask ,jsonify, request
from flask_sse import sse
from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app)
app.config["REDIS_URL"] = "redis://:p1997d415c09fe8b35f5553693ddbde63d698d0c462655d89c69b75da7363b052@ec2-44-197-6-129.compute-1.amazonaws.com:9629"

# configura o SSE com o path /event a ser escutado pelo cliente
app.register_blueprint(sse, url_prefix='/event')

caronas = []
interessados = []
id_carona = 1
id_interessado = 1

# configura os métodos de notificação para um evento e cliente específico (conforme o channel)

def notificar_subscribe_carona(channel, message):
    print('subscribeCaronasNovas')
    with app.app_context():
        sse.publish(message, type='subscribeCaronasNovas', channel=channel)
        print("Event subscribeCaronasNovas published at ",datetime.datetime.now())


def notificar_subscribe_interessados(channel, message):
    print('subscribeInteressadosNovos')
    with app.app_context():
        sse.publish(message, type='subscribeInteressadosNovos', channel=channel)
        print("Event subscribeInteressadosNovos published at ",datetime.datetime.now())


# a seguir, configura os endpoints consumidos pelo cliente

@app.route('/')
def index():
    return jsonify(hello_world())


@app.route('/consultarcarona', methods=['GET', 'POST'])
def consultar_carona_route():
    print('consultarcarona!')
    data = request.get_json()
    result = consultar_carona( data['origem'], data['destino'], data['data'])  
    return jsonify(result)

    
@app.route('/cadastrarcarona', methods=['GET', 'POST'])
def cadastrar_carona_route():
    print('cadastrarcarona!')
    data = request.get_json()
    result_cadastro = cadastrar_carona(data['channel'], data['nome'], data['contato'], data['origem'], data['destino'], data['data'], data['num_passageiros']) 
    result_notificacao = check_interessados_existentes(data['origem'], data['destino'], data['data'])
    if len(result_notificacao):
        for interessado in result_notificacao:
            message = f"o usuário {interessado['nome']} cadastrou uma carona que satisfaz seu interesse de id {interessado['id']}! segue o contato: {interessado['contato']}"
            notificar_subscribe_carona(interessado['channel'], message)
    return jsonify(result_cadastro)

    
@app.route('/cadastrarinteresse', methods=['GET', 'POST'])
def cadastrar_interesse_route():
    print('cadastrarinteresse!')
    data = request.get_json()
    result_cadastro = cadastrar_interesse_carona(data['channel'], data['nome'], data['contato'], data['origem'], data['destino'], data['data'])  
    result_notificacao = check_caronas_existentes(data['origem'], data['destino'], data['data'])
    if len(result_notificacao):
        for carona in result_notificacao:
            message = f"o usuário {carona['nome']} tem interesse na sua carona de id {carona['id']}! segue o contato: {carona['contato']}"
            notificar_subscribe_interessados(carona['channel'], message)
    return jsonify(result_cadastro)

    
@app.route('/cancelarcarona', methods=['GET', 'POST'])
def cancelar_carona_route():
    print('cancelarcarona!')
    data = request.get_json()
    result = cancelar_carona(data['id']) 
    return jsonify(result)
    

@app.route('/cancelarinteresse', methods=['GET', 'POST'])
def cancelar_interesse_route():
    print('cancelarinteresse!')
    data = request.get_json()
    print(data)
    result = cancelar_interesse(data['id'])    
    print(result)
    return jsonify(result)


# a seguir, implementa os métodos com as regras de negócio da aplicação

# cadastra registro de novoa carona
def cadastrar_carona(channel, nome, contato, origem, destino, data, num_passageiros):
    global id_carona
    id = id_carona
    id_carona += 1
    caronas.append({ 'id': id, 'channel': channel, 'nome': nome, 'contato': contato, 'origem': origem, 'destino': destino, 'data': data, 'num_passageiros': num_passageiros})

    print(f'Carona de {origem} a {destino} em {data} cadastrada com sucesso')
    return f'Carona de {origem} a {destino} em {data} cadastrada com sucesso (id = {id})'

# cadastra registro de novo interesse em carona
def cadastrar_interesse_carona(channel, nome, contato, origem, destino, data):
    global id_interessado
    id = id_interessado
    id_interessado += 1
    interessados.append({ 'id': id, 'channel': channel, 'nome': nome, 'contato': contato, 'origem': origem, 'destino': destino, 'data': data })

    print(f'Interesse em carona de {origem} a {destino} em {data} cadastrado com sucesso')
    return f'Interesse em carona de {origem} a {destino} em {data} cadastrado com sucesso (id = {id})'


# verifica se existem registros de carona correspondentes a esse interesse
def check_caronas_existentes(origem, destino, data):
    caronas_match = []
    for carona in caronas:
        if carona['origem'] == origem and carona['destino'] == destino and carona['data'] == data:
            caronas_match.append(carona)
    return caronas_match

# verifica se existem registros de interesse correspondentes a essa carona
def check_interessados_existentes(origem, destino, data):
    interessados_match = []
    for interessado in interessados:
        if interessado['origem'] == origem and interessado['destino'] == destino and interessado['data'] == data:
            interessados_match.append(interessado)
    return interessados_match


# verifica quantas caronas existentes atendem as especificações passadas na consulta
def consultar_carona(origem, destino, data):
    if len(caronas):
        total_caronas = 0
        for carona in caronas:
            if carona['origem'] == origem and carona['destino'] == destino and carona['data'] == data:
                total_caronas += 1
        return f'Existem {total_caronas} caronas de {origem} a {destino} na data {data}'
    else:
        return f'Não existem caronas cadastradas de {origem} a {destino} na data {data}'


# remove esse cliente da lista de interessados em receberem notificação de caronas cadastradas que atendam a esse interesse
def cancelar_interesse(id):
    id = int(id)
    if len(interessados) >= id:
        interessados.pop(id-1)
        return f'Interesse de id {id} cancelado com sucesso'
    return f'Não existe interesse de id {id} para cancelar'

# remove esse cliente da lista de interessados em receberem notificação de clientes interessados nessa carona
def cancelar_carona(id):
    id = int(id)
    if len(caronas) >= id:
        caronas.pop(id-1)
        return f'Carona de id {id} cancelado com sucesso'
    return f'Não existe carona de id {id} para cancelar'


def hello_world():
    return 'hello world'



if __name__ == '__main__':
   app.run(debug=True,host='0.0.0.0',port=5000)
