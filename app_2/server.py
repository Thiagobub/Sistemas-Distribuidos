######################################
# Universidade Tecnológica Federal do Paraná
# Sistemas Distribuídos
# Alunos: Juliana Rodrigues e Thiago Bubniak
# Engenharia de Computação
# Aplicação 2 - Serviços web
########################################

from __future__ import print_function

from flask import Flask, json, request, Response
from flask_sse import sse
from flask_cors import CORS
from flask_restful import Resource, Api, reqparse
import pandas as pd
import ast

from datetime import datetime
import threading

import requests
import sseclient
import time

from werkzeug.datastructures import MIMEAccept

# configura server
app = Flask(__name__)
CORS(app)
app.config["REDIS_URL"] = "redis://localhost"
app.register_blueprint(sse, url_prefix='/event')
api = Api(app)

# arquivos para armazenar usuários e enquetes
users_path = 'users.json'                 # User -> [remote_ref, public key]
enquetes_path = 'enquetes.json'           # Enquete -> [user1, user2, ...]


class Publisher(Resource):
    '''
        Classe Publisher - responsável por armazenar as chaves públicas dos usuários e fazer o controle das 
        enquetes, assim como seus status
    '''
    def __init__(self):

        #inicializa o publisher com uma thread, tendo a função start como trigger
        self.check()
    
    def get_users(self):
        '''
            open json file and return its data
        '''

        with open(users_path, 'r+') as f:
            data = json.load(f)
            f.close()

        return data

    def update_users(self, data):
        '''
            update json file with data 
        '''
        with open(users_path, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.close()

    def get_enquetes(self):
        '''
            open json file and return its data
        '''
        with open(enquetes_path, 'r+') as f:
            data = json.load(f)
            f.close()

        return data

    def update_enquetes(self, data):
        '''
            update json file with data
        '''
        
        with open(enquetes_path, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.close()


    def get(self):
        """
            Retorna as informações da enquete que o usuário solicitar no argumento 'enquete'
        """
        parser = reqparse.RequestParser()

        parser.add_argument('channel', required=False)
        parser.add_argument('user', required=True)
        parser.add_argument('request', required=True)
        parser.add_argument('enquete', required=False)

        args = parser.parse_args()

        # se o usuário deseja visitar um método
        if args['request'] == 'visit':
            # abre o arquivo json de usuários para ver se o user já está cadastrado
            data = self.get_users()
            
            # caso o usuário não esteja cadastrado, então cadastra
            if args['user'] not in data:
                data[args['user']] = args['channel']
                self.update_users(data)
                # retorna mensagem de sucesso
                return 200, {
                            'Content-Type': 'text/event-stream',
                            'Cache-Control': 'no-cache',
                            'Connection': 'keep-alive',
                            }
            else:
                # caso um usuário que já está cadastrado tente visitar o server, retorna mensagem de erro
                print("Usuario ja cadastrado!")
                return 401

        # se o usuário deseja obter info sobre uma enquete
        elif args['request'] == 'get info':
            # abre o arquivo json de enquetes para carregar as enquetes cadastradas
            data = self.get_enquetes()
            
            # caso a enquete desejada esteja na lista
            if args['enquete'] in data.keys() and args['enquete']:
                # caso o usuário esteja apto a votar naquela enquete
                if args['user'] in data[args['enquete']]['votantes']:
                    # retorna mensagem de sucesso
                    return json.dumps({'request': data[args['enquete']]}), 200
                # caso o usuário não possa votar naquela enquete
                else:
                    # retorna mensagem de acesso negado à enquete
                    print("Usuario nao encontrado na lista de votantes da enquete")
                    return 401
            # caso a enquete não esteja na lista
            else:
                # retorna mensagem de enquete não encontrada
                print("A enquete solicitada nao foi encontrada")
                return 404
        # caso o usuário passe algo diferente de visit/get info, retorna msg de argumento inválido
        else:
            print("Argumento do request invalido")
            return 406

    def post(self):
        """
            Posta uma nova enquete 
        """
        parser = reqparse.RequestParser()  # initialize

        parser.add_argument('user', required=True)  # add arguments
        parser.add_argument('enquete', required=True)
        parser.add_argument('local', required=True)
        parser.add_argument('limite', required=True)
        parser.add_argument('votos', required=True)

        args = parser.parse_args()  # parse arguments to dictionary

        # carrega todas as enquetes cadastradas
        data = self.get_enquetes()
       
        votos = {}
        # contabiliza a quantidade de votos para cada enquete
        for t in ast.literal_eval(args['votos']):
            votos[t] = 0

        # armazena os dados da enquete
        enquete = { 'local': args['local'],
                    'limite': args['limite'],
                    'votos': votos,
                    'votantes': [],
                    'status': 'Em andamento'}

        data[args['enquete']] = enquete
        
        # atualiza json com nova enquete
        self.update_enquetes(data)
        
        # notifica os clientes sobre nova enquete
        data = self.get_enquetes()
        sse.publish({'message': f"enquetes ativas: {data.keys()}"}, type='publish')

        return 200

    def put(self):
        """
            Cadastra voto em enquete 
        """
        parser = reqparse.RequestParser()

        parser.add_argument('user', required=True)
        parser.add_argument('enquete', required=True)
        parser.add_argument('voto', required=True)

        args = parser.parse_args()

        # carrega os dados sobre as enquetes
        data = self.get_enquetes()
       
        # verifica se a enquete está cadastrada
        if args['enquete'] in data.keys():
            # verifica se o status da enquete
            if data[args['enquete']]['status'] == 'Em andamento':
                # caso ela esteja em andamento e a opção desejada esteja disponível
                if args['voto'] in data[args['enquete']]['votos'].keys():
                    # cadastra voto
                    data[args['enquete']]['votos'][args['voto']] += 1
                    # cadastra o usuário como votante
                    if args['user'] not in data[args['enquete']]['votantes']:
                        data[args['enquete']]['votantes'].append(args['user'])
                else:
                    print("A opcao de voto nao esta disponivel")
                    return 404
            else:
                print("A enquete solicitada ja esta encerrada")
                return 401
        else:
            print("A enquete solicitada nao foi encontrada")
            return 404

        # atualiza json
        self.update_enquetes(data)
       
        print("Voto cadastrado!")
        return 200

    #@app.route('/abroba')
    def notify(self, user, msg):
        #return Response(msg, mimeetype="text/event-stream")
        channel = 'channel'
        with app.app_context():
            sse.publish(msg, type='publish', channel=user)
            print("Evento publish publicado às ",datetime.now())

    @app.route('/stream')
    def stream():
        def eventStream():
            while True:
                # wait for source data to be available, then push it
                yield 'data: {}\n\n'.format(get_message())
        return Response(eventStream(), mimetype="text/event-stream")
                          
    def check(self):
        threading.Thread(target=self._check).start()

    def _check(self):
        '''
        Método principal do publisher, verifica os status das enquetes e notifica os usuários 
        '''

        # a todo momento, verifica se existem enquetes ativas e, para cada uma delas, verifica seu status
        while(1):
            # carrega enquetes
            enquetes = self.get_enquetes()
            time.sleep(2)

            # carrega users
            users = self.get_users()
            time.sleep(1)
            
            if len(enquetes) > 0:
                for enquete_name, values in enquetes.items():
                    # para cada enquete na lista, verifica se todos os usuários já votaram ou se o tempo da 
                    # enquete já encerrou
                    limiteDatetime = datetime.strptime(values['limite'], '%Y-%m-%d_%H:%M')
                    msg = f"""\nEnquete encerrada!
                                    Titulo: {enquete_name}
                                    Local: {values['local']}
                                    Data final: {values['limite']}
                                    Votos: {values['votos']}
                                    Votantes: {values['votantes']}
                                    Status: {values['status']}
                                    """
                    # se a enquete acabar porque todos os usuários já votaram
                    if (len(values['votantes']) == len(users.keys()) and (values['status'] == 'Em andamento')):
                        print(f"{enquete_name} encerrada!")
                        enquetes[enquete_name]['status'] = 'Encerrada'
                        # atualiza json
                        self.update_enquetes(enquetes)
                        
                        # notifica todos os usuários sobre o status das enquetes nas quais eles estão cadastrados
                        for u in users.keys():
                            self.notify(user=u, msg={'message': msg})
                    # se a enquete acabar por tempo
                    elif ((values['status'] == 'Em andamento') or (datetime.now() >= limiteDatetime)):
                        print(f"{enquete_name} encerrada!")
                        enquetes[enquete_name]['status'] = 'Encerrada'
                        # atualiza json
                        self.update_enquetes(enquetes)
                         # notifica somente os usuários que cadastraram voto na enquete
                        for u in values['votantes'].keys():
                            self.notify(user=u, msg={'message': msg})


api.add_resource(Publisher, '/users')

if __name__ == '__main__':
    data = {}
    # limpa os arquivos com usuários e enquetes
    with open(users_path, 'w') as f:
        json.dump(data, f)
    with open(enquetes_path, 'w') as f:
        json.dump(data, f)
    # inicializa o server
    app.run(host='0.0.0.0', port=5000)