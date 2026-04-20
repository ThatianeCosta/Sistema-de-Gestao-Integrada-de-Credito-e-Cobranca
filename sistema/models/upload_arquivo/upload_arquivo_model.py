from sistema.models.base_model import BaseModel, db

class UploadArquivoModel(BaseModel):
    '''
    Model responsável por armazenar o registro de todos
    os arquivos que for feito no sistema.
    '''
    __tablename__ = 'upload_arquivo'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    nome = db.Column(db.String(255))
    caminho = db.Column(db.String(255))
    extensao = db.Column(db.String(8))
    tamanho = db.Column(db.Float)

    def __init__(
            self, nome, caminho, extensao, tamanho
    ):
        self.nome = nome
        self.caminho = caminho
        self.extensao = extensao
        self.tamanho = tamanho

    @classmethod
    def obter_arquivo_por_id(cls, id):
        return cls.query.filter(
            cls.id == id,
            cls.deletado == 0
        ).first()