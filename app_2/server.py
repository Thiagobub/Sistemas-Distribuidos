from __future__ import print_function

from flask import Flask, json, request
from flask_sse import sse
from flask_cors import CORS
from flask_restful import Resource, Api, reqparse
import pandas as pd
import ast

from base64 import b64decode,b64encode
from datetime import datetime
import threading

from Crypto.Hash import SHA384
from Crypto.Signature import pkcs1_15
from Crypto.PublicKey import RSA



app = Flask(__name__)
CORS(app)
app.config["REDIS_URL"] = "redis://localhost"
app.register_blueprint(sse, url_prefix='/event')
api = Api(app)

users_path = 'users.json'                 # User -> [remote_ref, public key]
enquetes_path = 'enquetes.json'              # Enquete -> [user1, user2, ...]


class Publisher(Resource):
    '''
    Classe Publisher - responsável por armazenar as chaves públicas dos usuários e fazer o controle das 
    enquetes, assim como seus status
    '''
    def __init__(self):
        self.flag_enquete = False
        
        # inicializa o publisher com uma thread, tendo a função start como trigger
        #self.check()
    
    def get(self):
        """
            Pega informações da enquete que o usuário quer - Pronto!
        """
        parser = reqparse.RequestParser()

        parser.add_argument('channel', required=True)
        parser.add_argument('user', required=True)
        parser.add_argument('request', required=True)
        parser.add_argument('enquete', required=False)

        args = parser.parse_args()

        if args['request'] == 'visit':
            with open(users_path, 'r+') as f:
                data = json.load(f)
                f.close()

            if args['user'] not in data:
                data[args['user']] = args['channel']
                with open(users_path, 'w') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                    f.close()
                    print(200)
                return 200
            else:
                print(401)
                return 401

        elif args['request'] == 'get_info':
            with open(enquetes_path, 'r+') as f:
                data = json.load(f)
                f.close()
            
            if args['enquete'] in data.keys() and args['enquete']:
                if args['user'] in data[args['enquete']]['votantes']:
                    print(200)
                    return json.dumps({'request': data[args['enquete']]})
                else:
                    print(401)
                    return 401
            else:
                print(404)
                return 404

        else:
            print(406)
            return 406

    def post(self):
        """
            Posta uma nova enquete - Pronto!
        """
        parser = reqparse.RequestParser()  # initialize

        parser.add_argument('user', required=True)  # add arguments
        parser.add_argument('enquete', required=True)
        parser.add_argument('local', required=True)
        parser.add_argument('limite', required=True)
        parser.add_argument('votos', required=True)

        args = parser.parse_args()  # parse arguments to dictionary

        with open(enquetes_path, 'r+') as f:
            data = json.load(f)
            f.close()

        votos = {}
        for t in ast.literal_eval(args['votos']):
            votos[t] = 0

        enquete = { 'local': args['local'],
                    'limite': args['limite'],
                    'votos': votos,
                    'votantes': [args['user']],
                    'status': 'Em andamento'}

        data[args['enquete']] = enquete

        with open(enquetes_path, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.close()

        # notificando clientes sobre nova enquete
        with open(enquetes_path, 'r') as f:
            data = json.load(f)
            sse.publish({'message': f"enquetes ativass: {data.keys()}"}, type='publish')
            f.close()

        return 200

    def put(self):
        """
            Coloca voto em enquete - Pronto!
        """
        parser = reqparse.RequestParser()

        parser.add_argument('user', required=True)
        parser.add_argument('enquete', required=True)
        parser.add_argument('voto', required=True)

        args = parser.parse_args()

        with open(enquetes_path, 'r+') as f:
            data = json.load(f)
            f.close()
        
        if args['enquete'] in data.keys():
            if data[args['enquete']]['status'] == 'Em andamento':
                if args['voto'] in data[args['enquete']]['votos'].keys():
                    data[args['enquete']]['votos'][args['voto']] += 1

                    if args['user'] not in data[args['enquete']]['votantes']:
                        data[args['enquete']]['votantes'].append(args['user'])
                else:
                    return 404
            else:
                return 401
        else:
            return 404

        with open(enquetes_path, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.close()

        return 200

    def notifica_user(channel, message):
        print('Notificando nova enquete')
        #sse.publish


api.add_resource(Publisher, '/users')

if __name__ == '__main__':
    data = {}
    with open(users_path, 'w') as f:
        json.dump(data, f)
    with open(enquetes_path, 'w') as f:
        json.dump(data, f)
    app.run(host='0.0.0.0', port=5000)










