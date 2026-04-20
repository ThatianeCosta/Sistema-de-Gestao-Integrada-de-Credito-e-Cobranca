from sistema.models.base_model import BaseModel, db
from sistema import login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin 


# Pega o usuário que está logado
@login_manager.user_loader
def get_user(user_id):
    return UsuarioModel.query.filter_by(id=user_id).first()

class UsuarioModel(BaseModel, UserMixin):
    '''
    Model para registro de Usuários e suas características
    '''
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    sobrenome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    senha = db.Column(db.String(255), nullable=False)

    # Relacionamento 1-1 com a Tabela 'role'
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    role = db.relationship('RoleModel', backref=db.backref('usuario', lazy=True))

    # Relacionamento 1-1 com a tabela 'upload_arquivo'
    foto_perfil_id = db.Column(db.Integer, db.ForeignKey('upload_arquivo.id'))
    foto_perfil = db.relationship('UploadArquivoModel', backref=db.backref('usuario'))

    ativo = db.Column(db.Boolean, nullable=False, default=True)

    def __init__(
            self, nome, sobrenome, email, telefone,
            senha, role_id, foto_perfil_id, ativo
    ):
        self.nome = nome
        self.sobrenome = sobrenome
        self.email = email
        self.telefone = telefone
        self.senha = generate_password_hash(senha)
        self.role_id = role_id
        self.foto_perfil_id = foto_perfil_id
        self.ativo = ativo

    def verificar_senha(self, senha):
        return check_password_hash(self.senha, senha)

    @classmethod
    def obter_usuario_por_email(cls, email):
        return cls.query.filter(
            cls.email == email,
            cls.deletado == 0
        ).first()

    @classmethod
    def obter_todos_usuarios(cls):
        return cls.query.filter(
            cls.deletado == 0
        ).order_by(cls.nome).all()