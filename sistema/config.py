#----------------------------Configurações Gerais ------------------------------------#
SECRET_KEY = 'todos-queassistirem-esse-curso-vao-vencer-na-vida'
DEBUG = True    # Para recarregar tudo ao atualizar a página


# -------------------------------Banco de Dados----------------------------------------#
DB_USERNAME = 'joao'
DB_PASSWORD = 'joao123'
DB_SERVER = 'localhost'
DB_DATABASE = 'local_gestao_emprest'

# No seu arquivo config.py
# Adicione +pymysql após o mysql
SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_SERVER}/{DB_DATABASE}'
SQLALCHEMY_TRACK_MODIFICATIONS = True    # quando alteral alguma coisa na migration, altera no DB
