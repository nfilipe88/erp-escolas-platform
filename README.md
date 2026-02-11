# erp-escolas-platform
PLATAFORMA INTEGRADA DE GESTÃO ESCOLAR
backend/
├── app/
│   ├── __init__.py  (vazio, só para dizer que é um pacote)
│   ├── database.py  (conexão)
│   └── models.py    (tabelas)
├── main.py          (ponto de entrada)
├── venv/
└── alembic/

No teu terminal (com o ambiente virtual ativo), executa:

Bash
pip install alembic
2. Iniciar o Alembic
Na raiz do projeto (onde está o main.py), executa:

Bash
alembic init alembic
Isto vai criar um ficheiro alembic.ini e uma pasta alembic/.
4. Criar a Primeira Migração (Initial)
Agora que o Alembic consegue ver os teus modelos e a tua base de dados, vamos criar a "fotografia" inicial do sistema.

No terminal:

Bash
alembic revision --autogenerate -m "Migracao Inicial"
O que vai acontecer:

O Alembic vai comparar os teus modelos (class Aluno...) com a base de dados real.

Vai criar um ficheiro em alembic/versions/ com as instruções para criar as tabelas.

⚠️ Verifica o ficheiro criado: Abre o ficheiro novo na pasta versions. Vê se a função upgrade() tem os comandos op.create_table(...).

5. Aplicar a Migração
Para criar as tabelas efetivamente na base de dados (ou atualizar o estado do versionamento):

Bash
alembic upgrade head