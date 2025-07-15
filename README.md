
# Boleto Service

API RESTful para geração, reemissão e reprocessamento de boletos bancários, com persistência em MongoDB e uso de Redis para fila de processamento.

---

## 📌 Tecnologias

- **Python 3.11**
- **FastAPI**
- **MongoDB (pymongo)**
- **Redis (redis-py)**
- **Pytest** – testes automatizados
- **Docker + Docker Compose**
- **GitHub Actions** – CI com execução de testes

---

## 🚀 Funcionalidades

### 🔸 POST `/boletos`

Gera um novo boleto com os seguintes dados:

- `nome`
- `cpf`
- `valor`
- `vencimento`

Além disso, o sistema gera:
- `codigo` único
- `linha_digitavel` simulada

O boleto é salvo com status `"enviado"`.

---

### 🔸 GET `/boletos/{codigo}`

Busca um boleto existente pelo código gerado anteriormente.

---

### 🔸 POST `/boletos/{codigo}/reprocessar`

Se o boleto tiver status `"erro"`, ele será reenviado para a fila Redis `fila_reprocessamento`, simulando reprocessamento.

---

## ⚙️ Como rodar localmente

### Pré-requisitos

- Python 3.11
- Docker e Docker Compose

### Setup

```bash
# Clonar o repositório
git clone https://github.com/DandaraEmiliano/boleto-service.git
cd boleto-service

# Subir MongoDB e Redis
docker-compose up -d

# Criar ambiente virtual e instalar dependências
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Rodar a aplicação
uvicorn app.main:app --reload
```

Acesse a documentação Swagger em:  
👉 `http://localhost:8000/docs`

---

## 🧪 Executar testes

```bash
pytest
```

---

## 🔄 Integração Contínua

O pipeline de CI está configurado via **GitHub Actions** e executa automaticamente os testes em cada `push` ou `pull_request`.

---

## 📂 Estrutura do Projeto

```
boleto-service/
├── app/
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── services/
│   └── main.py
├── tests/
│   └── unit/
├── docker-compose.yml
├── requirements.txt
├── .github/workflows/ci.yml
└── README.md
```

---

## 👩🏻‍💻 Autora

**Dandara Emiliano**  
[GitHub](https://github.com/DandaraEmiliano) · [LinkedIn](https://linkedin.com/in/dandaraemiliano)

---

## 📝 Licença

Este projeto está sob a licença MIT.
