# MediLembre

Aplicação web para controle de medicamentos, voltada para idosos e cuidadores.

## Stack

- **Back-end:** Python / Flask + SQLite + APScheduler
- **Front-end:** React.js
- **Notificações:** E-mail (Flask-Mail)
- **Relatórios:** PDF gerado com ReportLab

## Início rápido

### Back-end

```bash
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env           # edite com suas configurações
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

## Funcionalidades

- Cadastro de múltiplos pacientes por cuidador
- Cadastro de medicamentos com horários, dose e frequência
- Doses do dia com confirmação ("Tomei" / "Pular")
- Controle de estoque com alerta de baixo estoque
- Histórico de adesão ao tratamento
- Exportação de relatório em PDF para consultas médicas
- Lembretes por e-mail nos horários programados
- Interface acessível com fontes grandes e alto contraste

## API Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | /api/auth/register | Cadastro |
| POST | /api/auth/login | Login |
| GET | /api/patients/ | Listar pacientes |
| POST | /api/patients/ | Criar paciente |
| GET | /api/medications/patient/:id | Medicamentos do paciente |
| POST | /api/medications/patient/:id | Criar medicamento |
| GET | /api/doses/today/:patient_id | Doses de hoje |
| POST | /api/doses/confirm/:log_id | Confirmar dose |
| POST | /api/doses/skip/:log_id | Pular dose |
| GET | /api/doses/history/:patient_id | Histórico |
| GET | /api/reports/pdf/:patient_id | Exportar PDF |
