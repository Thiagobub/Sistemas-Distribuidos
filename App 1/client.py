######################################
# Universidade Tecnológica Federal do Paraná
# Sistemas Distribuídos
# Alunos: Juliana Rodrigues e Thiago Bubniak
# Engenharia de Computação
# Aplicação 1 - Middleware com Pyro
########################################

from __future__ import print_function
import sys
import threading

import Pyro4
import Pyro4.util

from Crypto.Hash import SHA384
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Signature import pkcs1_15

sys.excepthook = Pyro4.util.excepthook # faz aparecer as msg de erro do servidor

class Subscriber():
    '''
    Classe responsável pela comunicação dos usuários com o server (publisher + subscriber)
    '''
    def __init__(self):
        '''
        Coleta o nome do usuário e gera as chaves pública e privada para cada um deles
        '''
        self.server = Pyro4.core.Proxy("PYRONAME:example.publisher")
        self.name = input("Informe seu nome: ")
        self.abort = 0
        self.enquetes = []

        # Gerar chave pública e privada
        random_seed = Random.new().read
        self.private_key = RSA.generate(1024, random_seed)
        self.public_key = self.private_key.publickey()
        self.signature = pkcs1_15.new(self.private_key)

    def start(self):
        '''
        Conecta o usuário ao servidor (visit) informando que há um novo usuário no sistema
        '''
        print(f"Entering the system.")
        # passar o nome, chave pública e referencia
        self.server.visit(self.name, self.public_key.exportKey(), self)
        self.menu()
        
        self.enquetes = self.server.getEnquetes()
        print(f'Enquetes ativas: {self.enquetes}')

    def menu(self):
        '''
        Método responsável por mostrar ao usuário quais são as opções de interação com o sistema
        '''
        while(1):
            print('''1 - Cadastrar enquete\n2 - Cadastrar voto em enquete\n3 - Consultar enquete\n
            ''')
            n = input('Escolha uma das opções acima: ')
            if n == '1':
                titulo = input('Informe o titulo da enquete: ')
                local = input('Informe o local do evento: ')
                tempo = input('Informe datas e horários possíveis do evento (yyyy-mm-dd_hh:mm, yyyy-mm-dd_hh:mm, ...): ')
                limite = input('Informe data limite de votação (yyyy-mm-dd_hh:mm): ')
                print(self.server.setEnquete(self.name, titulo, local, tempo, limite))
            if n == '2':
                titulo = input("Informe o titulo da enquete para votar: ")
                tempo = input("Informe data e horário que deseja participar (yyyy-mm-dd_hh:mm): ")
                print(self.server.cadastraVoto(self.name, titulo, tempo))
                
            if n == '3':
                titulo = input('Informe o titulo da enquete: ')

                h = SHA384.new(bytes(titulo, encoding='utf-8'))
                
                print(self.server.consultaEnquete(self.name, self.signature.sign(h), titulo))

    @Pyro4.expose
    def notify(self, msg):
        '''
        Método que informa ao usuário o status das enquetes na qual ele está cadastrado
        '''
        if 'Enquete nova' in msg:
            print(msg)
        elif 'Enquete encerrada' in msg:
            print(msg)

# Daemon threads são responsáveis por rodar um bloco de código no background e não travar a execução
# do código principal. 
class DaemonThread(threading.Thread):
    def __init__(self, subscriber):
        threading.Thread.__init__(self)
        self.subscriber = subscriber
        self.setDaemon(True)

    def run(self):
        with Pyro4.core.Daemon() as daemon:
            daemon.register(self.subscriber)
            daemon.requestLoop(lambda: not self.subscriber.abort)


#uri = nameserver.lookup
# passa a uri pro proxy
s = Subscriber()
daemonthread = DaemonThread(s)
daemonthread.start()
s.start()
