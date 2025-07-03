# 📄 Boleto Service

API RESTful para geração e reemissão de boletos bancários, com persistência em MongoDB.

---

## ✅ Funcionalidades Implementadas

- **POST /boletos**  
  Gera um boleto com dados enviados (nome, CPF, valor, vencimento).  
  Gera um código único e linha digitável simulada.  
  Salva os dados no MongoDB.

- **GET /boletos/{codigo}**  
  Busca um boleto salvo com base no código gerado anteriormente.

---

## 🧱 Tecnologias Utilizadas

- **Python 3.13**
- **FastAPI**
- **MongoDB** (via Docker)
- **Pymongo**
- **Docker Compose**

---

## 📦 Estrutura de Pastas

```
boleto-service/
├── app/
│   ├── api/                
│   │   └── boleto.py
│   ├── core/               
│   │   └── mongo.py
│   ├── models/             
│   ├── schema/             
│   │   └── boleto.py
│   ├── services/           
│   │   └── boleto_service.py
│   └── main.py             
├── docker-compose.yml      
├── requirements.txt        
└── .gitignore
```

---

## ▶️ Como rodar localmente

1. Subir o MongoDB:
```bash
docker compose up -d
```

2. Ativar o ambiente virtual e instalar dependências:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Rodar a aplicação:
```bash
uvicorn app.main:app --reload
```

4. Acessar a documentação Swagger:
```
http://localhost:8000/docs
```

---

## 🔃 Exemplo de uso

### POST /boletos

```json
{
  "nome": "Dandara",
  "cpf": "12345678900",
  "valor": 150.0,
  "vencimento": "2025-07-10"
}
```

### GET /boletos/{codigo}

Retorna boleto persistido com base no código gerado.

---
## 👩🏻‍💻 Autora

**Dandara Emiliano**  
[GitHub](https://github.com/DandaraEmiliano) · [LinkedIn](https://linkedin.com/in/dandaraemiliano)

---

## 📝 Licença

Este projeto está sob a licença MIT.
