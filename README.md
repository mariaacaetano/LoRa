# AgroSense LoRaWAN

Plataforma web em Django para simulação e monitoramento de sensores de temperatura e umidade em ambientes de produção animal.

## Requisitos

- Python 3.10 ou superior
- `pip` e suporte à criação de ambientes virtuais
- Git

## Instalação

Clone o repositório e entre no diretório do projeto:

```bash
git clone <URL_DO_REPOSITORIO>
cd LoRa
```

Crie e ative um ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

No Windows PowerShell, use:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Instale as dependências e prepare o banco de dados:

```bash
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py reset_historico
```

Inicie a aplicação:

```bash
python manage.py runserver
```

Acesse [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

## Usuários de demonstração

O comando `seed_demo` cria três usuários com a senha `123`:

| Usuário | Perfil |
| --- | --- |
| `gestor` | Visualiza o painel e recebe alertas em tempo real |
| `professor` | Visualiza o painel e os dados dos sensores |
| `pesquisador` | Consulta o histórico de monitoramento |

## Simulação

O botão **Iniciar simulação** gera uma leitura por sensor a cada dez segundos. A interface mantém as seis leituras mais recentes de cada ambiente. Em ciclos de seis iterações, um ou dois sensores variam gradualmente até gerar alertas demonstrativos, sem saltos bruscos entre leituras.

Para restaurar o conjunto mínimo de demonstração:

```bash
python manage.py reset_historico
```

## Documentação acadêmica

O artigo, o resumo expandido, as figuras e os demais artefatos acadêmicos ficam na branch `documentacao-academica`:

```bash
git switch documentacao-academica
```

## Produção

Antes de publicar a aplicação, defina uma `SECRET_KEY` segura, desative `DEBUG`, configure `ALLOWED_HOSTS`, altere as senhas de demonstração e utilize um servidor WSGI ou ASGI apropriado.
