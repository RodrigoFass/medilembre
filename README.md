# MediLembre 💊

Aplicação web para controle de medicamentos voltada para idosos, pacientes e cuidadores. Desenvolvida com Flask (back-end) e React (front-end), com design premium moderno.

## Stack

| Camada | Tecnologias |
|--------|-------------|
| **Back-end** | Python 3, Flask, SQLAlchemy, Flask-JWT-Extended, Marshmallow |
| **Banco de dados** | SQLite (via SQLAlchemy ORM) |
| **Agendamento** | APScheduler (geração de doses diárias, marcação de perdidas, lembretes) |
| **Notificações** | E-mail via Flask-Mail |
| **Relatórios** | PDF com ReportLab |
| **Front-end** | React.js, Axios, React Router |
| **Estilo** | CSS customizado com design system completo (variáveis CSS) |
| **Testes** | pytest + pytest-flask (suite com 19 testes) |

## Funcionalidades

- Autenticação segura com JWT (registro e login)
- Cadastro de múltiplos pacientes por cuidador
- Cadastro de medicamentos com horários, dose, frequência e instruções
- Controle de estoque com alerta de baixo estoque
- Doses do dia com ações **"Tomei"** / **"Pular"**
- Histórico de adesão com anel de progresso animado (SVG)
- Exportação de relatório em PDF para consultas médicas
- Lembretes automáticos por e-mail nos horários programados
- Interface responsiva, premium e acessível (320px → desktop)

## Início rápido

### Pré-requisitos

- Python 3.10+
- Node.js 18+

### Back-end

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac
pip install -r requirements.txt

copy .env.example .env         # Windows
# cp .env.example .env         # Linux/Mac
# Edite o .env com suas chaves e configurações de e-mail

python run.py
```

Servidor disponível em `http://localhost:5000`

### Front-end

```bash
cd frontend
npm install
npm start
```

App disponível em `http://localhost:3000`

### Testes

```bash
cd backend
python -m pytest tests/ -v
```

## Variáveis de ambiente

Copie `.env.example` para `.env` e preencha:

```env
FLASK_ENV=development
SECRET_KEY=sua-chave-secreta-minimo-32-chars
JWT_SECRET_KEY=outra-chave-secreta-minimo-32-chars
DATABASE_URL=sqlite:///medilembre.db

# Configurações de e-mail (opcional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=seu@email.com
MAIL_PASSWORD=sua-senha-de-app
MAIL_DEFAULT_SENDER=seu@email.com
```

## API Endpoints

### Autenticação
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/auth/register` | Cadastro de usuário |
| POST | `/api/auth/login` | Login |
| GET | `/api/auth/me` | Dados do usuário logado |

### Pacientes
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/patients/` | Listar pacientes |
| POST | `/api/patients/` | Criar paciente |
| GET | `/api/patients/:id` | Buscar paciente |
| PUT | `/api/patients/:id` | Editar paciente |
| DELETE | `/api/patients/:id` | Remover paciente |

### Medicamentos
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/medications/patient/:id` | Listar medicamentos |
| POST | `/api/medications/patient/:id` | Criar medicamento |
| PUT | `/api/medications/:id` | Editar medicamento |
| DELETE | `/api/medications/:id` | Remover medicamento |

### Doses
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/doses/today/:patient_id` | Doses de hoje |
| POST | `/api/doses/confirm/:log_id` | Confirmar dose |
| POST | `/api/doses/skip/:log_id` | Pular dose |
| GET | `/api/doses/history/:patient_id` | Histórico de adesão |

### Relatórios
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/reports/pdf/:patient_id` | Exportar PDF |

## Estrutura do projeto

```
medilembre/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy: User, Patient, Medication, DoseLog
│   │   ├── routes/          # Blueprints: auth, patients, medications, doses, reports
│   │   ├── schemas/         # Validação Marshmallow
│   │   ├── services/        # Scheduler (APScheduler) e notificações
│   │   └── __init__.py      # Application Factory (create_app)
│   ├── tests/               # Suite pytest com 19 testes
│   ├── config.py            # DevelopmentConfig / TestingConfig / ProductionConfig
│   ├── requirements.txt
│   └── run.py
└── frontend/
    ├── public/
    └── src/
        ├── components/      # Layout, DoseCard, PatientModal, MedicationModal
        ├── context/         # AuthContext (JWT)
        ├── pages/           # Login, Register, Dashboard, PatientDetail, History
        ├── services/        # Axios com interceptor 401
        └── index.css        # Design system com variáveis CSS
```
