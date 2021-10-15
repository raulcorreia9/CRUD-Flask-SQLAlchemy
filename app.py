from flask import Flask, request, Response
#Flask -> Criação de rotas da API
#Response -> Classe para tratar o retorno da API
#requeste -> Utilizado para tratar do body - POST
from flask_sqlalchemy import SQLAlchemy #Classe que trata com o banco de dados
import psycopg2 #Conexão com o PostgreSQL
import json

app = Flask(__name__) # definição da variavel app para fazer as routes
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:senha123@localhost:5432/crud_flask'

db = SQLAlchemy(app) #Conexão do SQLAlchemy com o app Flask

class Usuario(db.Model): #Montando tabela usuário, classe Usuario extendendo db.Model
    id = db.Column(db.Integer, primary_key = True)
    nome = db.Column(db.String(50))
    email = db.Column(db.String(100))

    def to_json(self):
        return{"id":self.id, "nome":self.nome, "email":self.email}

#db.create_all() -> criando tabelas | Abrir o terminal -> Python -> from app import db 
# -> db.create_all() evitar de criar algo que ja existe ao reiniciar API

#Find All
@app.route("/usuarios", methods = ["GET"])
def seleciona_usuarios():
    usuarios_object =  Usuario.query.all() # Como usuário extende db(SQLAlchemy), basta chamar o método query.all()
    usuarios_json = [usuario.to_json() for usuario in usuarios_object] # monta um vetor com cada usuario em forma de json vindo da query
    
    return gera_response(200, "usuarios", usuarios_json, "Listagem feita com sucesso!")

def gera_response(status, nome_conteudo, conteudo, mensagem = False): # Função que trata os responses dos métodos da API
    body = {}
    body[nome_conteudo] = conteudo

    if(mensagem):
        body["mensagem"] = mensagem

    # Transformando objeto python para um JSON apropriado | json.dumps()
    return Response(json.dumps(body), status = status, mimetype = "application/json")

#Find by ID
@app.route("/usuario/<id>", methods = ["GET"])
def seleciona_usuario(id):
    usuario_objeto = Usuario.query.filter_by(id = id).first() # Buscando usuário pelo ID
    usuario_json = usuario_objeto.to_json() # Convertendo para JSON

    return gera_response(200, "usuario", usuario_json, "Usuário encontrado com sucesso!")

#Create
@app.route("/usuario/create", methods = ["POST"])
def cria_usuario():
    body = request.get_json() # Capturando json vindo do request post

    #Try | Except para verificar a criação do usuário
    try:
        usuario_objeto = Usuario(nome = body["nome"], email = body["email"]) # atribuindo os valores vindos do body
        db.session.add(usuario) # Criando uma sessão e adicionando o novo usuário através do SQLAlchemy
        db.session.commit() # Comitando a ultima ação

        #usuario_json = usuario.to_json()

        return gera_response(201, "usuario", usuario_objeto.to_json(), "Usuário cadastrado com sucesso!")
    except Exception as e:
        print(e)
        return gera_response(400, "usuario", {}, "Erro ao criar novo usuário.")
    
#Update
@app.route("/usuario/<id>", methods = ["PUT"])
def atualiza_usuario(id):
    usuario_objeto = Usuario.query.filter_by(id = id).first() #Capturando usuário
    body = request.get_json()

    try:
        if("nome" in body):
            usuario_objeto.nome = body["nome"]
        if("email" in body):
            usuario_objeto.email = body["email"]
        
        db.session.add(usuario_objeto)
        db.session.commit()
        return gera_response(200, "usuario", usuario_objeto.to_json(), "Usuário atualizado com sucesso!")
    except Exception as e:
        return gera_response(400, "usuario", {}, "Erro ao atualizar usuário")

#Delete
@app.route("/usuario/<id>", methods = ["DELETE"])
def deleta_usuario(id):
    usuario_objeto = Usuario.query.filter_by(id = id).first()
    
    try:
        db.session.delete(usuario_objeto)
        db.session.commit()
        return gera_response(200, "usuario", usuario_objeto.to_json(), "Usuário deletado com sucesso!")
    except Exception as e:
        return gera_response(400, "usuario", {}, "Erro ao deletar usuário")

app.run() #Executando aplicação