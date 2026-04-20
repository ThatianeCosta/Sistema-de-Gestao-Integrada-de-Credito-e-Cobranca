from datetime import datetime
from pytz import timezone
from sistema import db

# Pegando o Fuso Horário de São Paulo
fuso_horario = timezone('America/Sao_Paulo')


class BaseModel(db.Model): 
    # Model base para registro de auditoria exclusão lógica
    __abstract__ = True
    data_cadastro = db.Column(
        db.DateTime, default=lambda: datetime.now(fuso_horario), nullable=False
    )
    data_alteracao = db.Column(
        db.DateTime, default=lambda: datetime.now(fuso_horario), nullable=False,
        onupdate=lambda: datetime.now(fuso_horario)
    )
    deletado = db.Column(db.Boolean, default=False, nullable=False)

    def salvar(self):
        db.session.add(self)
        db.session.commit()

    def excluir(self):
        self.deletado = True
        db.session.commit()
