# FastAPI + MongoDB (Motor) CRUD de Usuários

## Como rodar o projeto (Docker Compose)

1. **Clone o repositório:**
   ```bash
   git clone git@github.com:Alvarezgonca/api-crud-fastapi.git
   cd api-crud-fastapi
   ```

2. **Suba os serviços (API + MongoDB):**
   ```bash
   docker compose up --build
   ```

3. **Acesse a documentação Swagger:**
   - http://localhost:8000/docs

> Se quiser rodar localmente (sem Docker), ative sua venv, instale as dependências (`pip install -r requirements.txt`) e rode:
> ```bash
> uvicorn main:app --reload
> ```

## Endpoints

### POST /users
Cria um usuário.

**Exemplo de requisição:**
```json
{
  "name": "Ana",
  "email": "ana@email.com",
  "age": 22,
  "is_active": true
}
```
**Respostas:**
- 201: Usuário criado
- 409: E-mail já cadastrado
- 400: Dados inválidos

### GET /users
Lista usuários com filtros e paginação.

**Parâmetros opcionais:**
- `q`: busca por nome
- `min_age`, `max_age`: filtra por idade
- `is_active`: true/false
- `page`: página (default 1)
- `limit`: itens por página (default 10)

**Exemplo:**
```
GET /users?q=ana&min_age=18&is_active=true&page=1&limit=5
```

### GET /users/{id}
Busca usuário por id.
- 404: Não encontrado
- 400: ID inválido

### PUT /users/{id}
Atualiza usuário.
- 409: E-mail já cadastrado
- 404: Não encontrado
- 400: Dados inválidos

### DELETE /users/{id}
Remove usuário.
- 204: Sucesso
- 404: Não encontrado
- 400: ID inválido

## Exemplos de uso com curl

**Criar usuário:**
```bash
curl -X POST http://localhost:8000/users -H "Content-Type: application/json" -d '{"name":"Ana","email":"ana@email.com","age":22,"is_active":true}'
```

**Listar usuários:**
```bash
curl http://localhost:8000/users
```

**Buscar por nome e idade:**
```bash
curl "http://localhost:8000/users?q=ana&min_age=18"
```

**Buscar por id:**
```bash
curl http://localhost:8000/users/<id>
```

**Atualizar usuário:**
```bash
curl -X PUT http://localhost:8000/users/<id> -H "Content-Type: application/json" -d '{"name":"Ana Paula"}'
```

**Deletar usuário:**
```bash
curl -X DELETE http://localhost:8000/users/<id>
```

## Observações
- O campo `_id` sempre retorna como string.
- O campo `email` é único.
- Todos os endpoints podem ser testados no Swagger (http://localhost:8000/docs) ou Insomnia/Postman.
