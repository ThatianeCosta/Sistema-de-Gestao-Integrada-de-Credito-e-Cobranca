from sistema import db
from sistema.models.base_model import BaseModel
from sqlalchemy import asc


# from sistema.models.base_model import BaseModel, db


class RoleModel(BaseModel):
    '''
    Model responsável pelo registro de Cargos/Funções do sistema
    '''
    __tablename__ = 'role'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cargo = db.Column(db.String(100), nullable=False)

    def __init__(self, nome, cargo):
        self.nome = nome
        self.cargo = cargo

    @classmethod
    def obter_roles_asc_cargo(cls):
        roles = cls.query.filter(
            cls.deletado == 0
        ).order_by(
            asc(cls.cargo)
        ).all()   

        return roles

    @classmethod
    def obter_role_por_id(cls, id):
        role = cls.query.filter(
            cls.id == id
        ).first()
        return role
