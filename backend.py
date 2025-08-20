import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import bcrypt

# --- 1. CONFIGURAÇÃO INICIAL ---
app = Flask(__name__)
CORS(app)

# Configura o caminho do nosso banco de dados SQLite
# Ele irá procurar pelo arquivo 'usuarios.db' na mesma pasta do projeto
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'usuarios.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa a extensão SQLAlchemy para interagir com o banco de dados
db = SQLAlchemy(app)


# --- 2. MODELO DO BANCO DE DADOS ---
# Esta classe é o "molde" que representa nossa tabela 'usuarios' no código Python
class Usuario(db.Model):
    __tablename__ = 'usuarios'  # Garante que o nome da tabela seja 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Usuario {self.nome}>'


# --- 3. ROTAS DA NOSSA API ---

@app.route('/')
def index():
    return jsonify({"status": "Nosso backend está no ar!"})


# Nova rota para o cadastro de usuários
# methods=['POST'] significa que esta rota só aceita requisições do tipo POST (envio de dados)
@app.route('/registro', methods=['POST'])
def registro():
    # Pega os dados (JSON) que foram enviados na requisição
    dados = request.get_json()

    # Validação básica dos dados recebidos
    if not dados or not 'nome' in dados or not 'email' in dados or not 'senha' in dados:
        return jsonify({"status": "erro", "mensagem": "Dados incompletos"}), 400

    # Verifica se o e-mail já existe no banco de dados
    if Usuario.query.filter_by(email=dados['email']).first():
        return jsonify({"status": "erro", "mensagem": "Este e-mail já está cadastrado"}), 409

    # Criptografa a senha recebida antes de salvar
    senha_texto = dados['senha'].encode('utf-8')
    sal = bcrypt.gensalt()
    senha_hash = bcrypt.hashpw(senha_texto, sal).decode('utf-8')

    # Cria uma nova instância do nosso "molde" de usuário
    novo_usuario = Usuario(nome=dados['nome'], email=dados['email'], senha_hash=senha_hash)

    # Adiciona o novo usuário à sessão do banco de dados e salva (commit)
    try:
        db.session.add(novo_usuario)
        db.session.commit()
        # Se tudo deu certo, retorna uma mensagem de sucesso
        return jsonify({"status": "sucesso", "mensagem": "Usuário criado com sucesso!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "erro", "mensagem": f"Erro ao salvar no banco de dados: {e}"}), 500


# --- Bloco de Execução ---
if __name__ == '__main__':
    app.run(debug=True, port=5001)