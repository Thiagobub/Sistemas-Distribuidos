from __future__ import print_function
from base64 import b64decode,b64encode
from datetime import datetime

from Crypto.Hash import SHA384
from Crypto.Signature import pkcs1_15
from Crypto.PublicKey import RSA


from Pyro4.core import Daemon
import Pyro4

class Enquete():
    def __init__(self, titulo, local, tempo, limite):
        self.titulo = titulo
        self.local = local
        self.tempo = tempo
        self.limite = limite
        self.votos = {}
        self.votantes = []
        self.status = 'Em andamento'

@Pyro4.behavior(instance_mode='single') # ???
@Pyro4.expose # é permitido acessar a classe remotamente
class Publisher():
    def __init__(self):
        self.users = {} # User -> [remote_ref, public key]
        self.enquetes = {} # Enquete -> [user1, user2, ...]
        self.flag_enquete = False

    def getEnquetes(self):
        return [x.titulo for x in self.enquetes.keys()]

    def visit(self, name, public_key, user):
        public_key = b64decode(public_key['data'])

        print(f'Novo usuario: {name}')
        self.users[name] = [user, public_key]

    def setEnquete(self, name, titulo, local, tempo, limite):

        enquete = Enquete(titulo, local, tempo, limite)
        self.enquetes[enquete] = [name]
        print(f"{name} cadastrou nova enquete {titulo}")

        print(self.enquetes)

        # parece q da ruim chamar aqui, pois é o cliente q
        # vai estar chamando os métodos da galera
        # Vai ter q usar algo com o flag ali em outro canto do código
        for name, info in self.users.items():
            enquetes = self.getEnquetes()
            info[0].notify('Enquete nova', enquetes)
        return 'Nova enquete publicada!'

    def findEnquete(self, titulo):
        if titulo in self.getEnquetes():
            for enquete in self.enquetes.keys():
                if enquete.titulo == titulo:
                    return enquete
        else:
            return 0

    def cadastraVoto(self, name, titulo, tempo):

        ## Conferir se o usuário não está votando 2 vezes
        enquete = self.findEnquete(titulo)
        
        if enquete:
            if name not in enquete.votantes:
                if tempo in enquete.votos.keys():
                    enquete.votos[tempo] += 1
                else:
                    enquete.votos[tempo] = 1

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

        signed = b64decode(signed['data'])
        
        h = SHA384.new(bytes(titulo, encoding='utf-8'))
        key = RSA.importKey(self.users[name][1])

        try:
            pkcs1_15.new(key).verify(h, signed)
        except:
            print(f"{name} assinatura inválida!")
            return "Permissão negada"

        enquete = self.findEnquete(titulo)
        if enquete:
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
                print(f"{name} consultando enquete que não está cadastrado")
                return "Permissão negada!"
        else:
            print(f"{name} consultando enquete que não existe")
            return "Permissão negada!"


    def start(self):

        # Fica checando as enquetes que existem, se o tempo
        #  delas acabou ou se todos os usuários ja votaram
        while(1):
            for enquete in self.enquetes:
                if len(enquete.votos) > 2:
                    print("enquete teve 2 votos!!!")
            pass


Pyro4.Daemon.serveSimple({ Publisher: "example.publisher" }, ns = True) # ???
# ns = True diz pro pyro usar um servidor de nome pra registrar as classes
ns = Pyro4.locateNS()
uri = Daemon.register()
# uri = ...
# ....
# ns.register("example.warehouse", uri) # para registrar o servidor de nome


# @Pyro4.oneway # é um método que quando chamado remotamente, não espera return