# 🚀 Meetup Management API

API profissional para gerenciamento de eventos técnicos (Meetups), com sistema de autenticação, controle de vagas em tempo real e busca avançada. Desenvolvida com foco em performance assíncrona e segurança de dados.

## 🛠 Tecnologias e Ferramentas
- **FastAPI**
- **PostgreSQL**
- **SQLAlchemy**
- **Pydantic V2**
- **Bcrypt**
- **PyJWT**
- **Pytest**

## 📍 Endpoints da API

### Autenticação

| Método | Rota | Descrição |
| :--- | :--- | :--- |
| POST | `/login` | Login do usuário, retorna Token JWT Bearer |

### Usuários

| Método | Rota | Acesso | Descrição |
| :--- | :--- | :--- | :--- |
| POST | `/users` | Público | Cadastro de novo usuário (Organizador/Participante) |

### Eventos (Meetups)

| Método | Rota | Acesso | Descrição |
| :--- | :--- | :--- | :--- |
| GET | `/events` | Público | Lista eventos (Filtros: `search`, `skip`, `limit`) |
| POST | `/events` | Autenticado | Criar um novo evento com limite de vagas |
| PUT | `/events/{id}`| Dono | Atualizar dados do evento (Título, Data, Vagas) |
| DELETE| `/events/{id}`| Dono | Remover evento permanentemente |

### Inscrições

| Método | Rota | Acesso | Descrição |
| :--- | :--- | :--- | :--- |
| POST | `/events/{id}/register` | Autenticado | Inscrever-se (Valida duplicidade e vagas reais) |

---

## 🏃 Como Rodar o Projeto

1. **Subir a Infraestrutura (Postgres):**
   ```bash
   docker-compose up -d
   ```

2. **Preparar o Ambiente Python:**
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate  # Windows
   # source .venv/bin/activate # Linux/Mac
   pip install -r requirements.txt
   ```

3. **Iniciar o Servidor:**
   ```bash
   uvicorn main:app --reload
   ```

## 🧪 Como Testar

- **Documentação Interativa (Swagger):** Acesse http://127.0.0.1:8000/docs
- **Testes Automatizados:**
  ```bash
  python -m pytest
  ```

---

## 💡 Diferenciais Técnicos desta Implementação

- **Segurança:** Separação estrita entre modelos de banco e schemas de saída (Pydantic), garantindo que senhas e dados sensíveis nunca vazem na API.
- **Regras de Negócio:** Sistema inteligente de vagas que impede inscrições excedentes ou duplicadas no mesmo evento.
- **Escalabilidade:** Implementação de paginação (`skip`/`limit`) e busca parcial (`ilike`) para lidar com grandes volumes de dados de forma eficiente.
- **Clean Code:** Uso de gerenciadores de contexto para sessões de banco de dados e criptografia moderna com biblioteca `bcrypt` nativa.
