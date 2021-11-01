######################################
# Universidade Tecnológica Federal do Paraná
# Sistemas Distribuídos
# Alunos: Juliana Rodrigues e Thiago Bubniak
# Engenharia de Computação
# Aplicação 1 - Middleware com Pyro
########################################

from __future__ import print_function
from base64 import b64decode,b64encode
from datetime import datetime
import threading

from Crypto.Hash import SHA384
from Crypto.Signature import pkcs1_15
from Crypto.PublicKey import RSA

from Pyro4.core import Daemon
import Pyro4

class Enquete():
    '''
    Classe responsável pelo armazenamento das informações das enquetes
    '''
    def __init__(self, titulo, local, tempo, limite):
        self.titulo = titulo
        self.local = local
        self.tempo = tempo
        self.limite = datetime.strptime(limite, '%Y-%m-%d %H:%M')
        self.votos = {}
        self.votantes = []
        self.status = 'Em andamento'

@Pyro4.behavior(instance_mode='single')
@Pyro4.expose   # é permitido acessar a classe remotamente
class Publisher():
    '''
    Classe Publisher - responsável por armazenar as chaves públicas dos usuários e fazer o controle das 
    enquetes, assim como seus status
    '''
    def __init__(self):
        self.users = {}                 # User -> [remote_ref, public key]
        self.enquetes = {}              # Enquete -> [user1, user2, ...]
        self.flag_enquete = False

        # inicializa o publisher com uma thread, tendo a função start como trigger
        self.check()

    def getEnquetes(self):
        '''
        Recupera todas as enquetes cadastradas pelos usuários
        '''
        return [x.titulo for x in self.enquetes.keys()]

    def visit(self, name, public_key, user):
        '''
        Informa que um novo usuário se conectou ao sistema
        Cadastra o nome e a chave pública do usuário
        '''
        public_key = b64decode(public_key['data'])

        print(f'Novo usuario: {name}')
        self.users[name] = [user, public_key]

    def setEnquete(self, name, titulo, local, tempo, limite):
        '''
        Cadastra uma nova enquete no sistema
        '''
        enquete = Enquete(titulo, local, tempo, limite)
        self.enquetes[enquete] = [name]
        print(f"{name} cadastrou nova enquete {titulo}")

        for name, info in self.users.items():
            enquetes = self.getEnquetes()
            info[0].notify(f'\nEnquete nova! Enquetes ativas: {enquetes}')
        return 'Nova enquete publicada!'

    def findEnquete(self, titulo):
        '''
        Recupera enquete pelo nome
        '''
        if titulo in self.getEnquetes():
            for enquete in self.enquetes.keys():
                if enquete.titulo == titulo:
                    return enquete
        else:
            return 0

    def cadastraVoto(self, name, titulo, tempo):
        '''
        Cadastra o voto do usuário em determinada enquete
        Confere se o usuário não está votando 2 vezes na mesma enquete
        '''
        enquete = self.findEnquete(titulo)
        
        # verifica se a enquete existe
        if enquete:
            # caso ela ainda possa receber votos
            if enquete.status == 'Em andamento':
                if tempo in enquete.votos.keys():
                    enquete.votos[tempo] += 1
                else:
                    enquete.votos[tempo] = 1
                # insere o votante na lista de votantes da enquete
                enquete.votantes.append(name)
                if name not in self.enquetes[enquete]:
                    self.enquetes[enquete].append(name)
                
                print(f"{name} votou na enquete {titulo}.")
                return "Voto cadastrado!"
            else:
                print(f"{name} tentou votar 2 vezes na mesma enquete")
                return "Permissão negada! Voto já realizado."
        else:
            print(f"{name} tentou votar em uma enquete que não existe!")
            return "Enquete não existe!"
        

    def consultaEnquete(self, name, signed, titulo):
        '''
        Consulta o status de uma determinada enquete
        Só retorna o status da enquete na qual o usuário está cadastrado (sua chave pública está armazenada)
        '''

        # verifica se a assinatura corresponde à assinatura do usuário que está 
        # requisitando acesso à enquete
        signed = b64decode(signed['data'])
        h = SHA384.new(bytes(titulo, encoding='utf-8'))
        key = RSA.importKey(self.users[name][1])

        try:
            pkcs1_15.new(key).verify(h, signed)
        except:
            print(f"{name} assinatura inválida!")
            return "Permissão negada"
        
        # caso a assinatura seja válida, procura pela enquete em questão
        enquete = self.findEnquete(titulo)
        # caso a enquete exista
        if enquete:
            # caso o usuário seja um votante na enquete
            if name in self.enquetes[enquete]:
                print(f"{name} consultando informações da enquete {titulo}")
                return f"""
                    Titulo: {enquete.titulo}
                    Local: {enquete.local}
                    Quando: {enquete.tempo}
                    Data final: {enquete.limite}
                    Votos: {enquete.votos}
                    Votantes: {enquete.votantes}
                    Status: {enquete.status}
                """
            else:
                print(f"{name} consultando enquete que ele não está cadastrado")
                return "Permissão negada!"
        else:
            print(f"{name} consultando enquete que não existe")
            return "Permissão negada!"

    def check(self):
        threading.Thread(target=self._check).start()

    def _check(self):
        '''
        Método principal do publisher, verifica os status das enquetes e notifica os usuários 
        '''
        # a todo momento, verifica se existem enquetes ativas e, para cada uma delas, verifica seu status
        while(1):
            if len(self.enquetes) > 0:
                lista = list(self.enquetes.keys())
                for enquete in lista:
                    # para cada enquete na lista, verifica se todos os usuários já votaram ou se o tempo da 
                    # enquete já encerrou
                    if (((len(enquete.votantes) == len(self.users.keys())) or (datetime.now() >= enquete.limite))
                         and (enquete.status == 'Em andamento')):
                        print(f"{enquete.titulo} encerrada!")
                        enquete.status = 'Encerrada'
                        msg = f"""\nEnquete encerrada!
                                    Titulo: {enquete.titulo}
                                    Local: {enquete.local}
                                    Quando: {enquete.tempo}
                                    Data final: {enquete.limite}
                                    Votos: {enquete.votos}
                                    Votantes: {enquete.votantes}
                                    Status: {enquete.status}
                                    """
                        # notifica os usuários sobre o status das enquetes nas quais eles estão cadastrados
                        for u in self.enquetes[enquete]:
                            self.users[u][0].notify(msg)

# inicializa o server
Pyro4.Daemon.serveSimple({ Publisher: "example.publisher" }, ns = True)
# inicia o naming server
ns = Pyro4.locateNS()
uri = Daemon.register()