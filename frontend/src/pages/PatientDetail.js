import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import api from "../services/api";
import MedicationModal from "../components/MedicationModal";
import DoseCard from "../components/DoseCard";
import "./PatientDetail.css";

export default function PatientDetail() {
  const { id } = useParams();
  const [patient, setPatient] = useState(null);
  const [medications, setMedications] = useState([]);
  const [todayDoses, setTodayDoses] = useState([]);
  const [showMedModal, setShowMedModal] = useState(false);
  const [editMed, setEditMed] = useState(null);
  const [tab, setTab] = useState("hoje");
  const [loading, setLoading] = useState(true);

  const load = async () => {
    try {
      const [patientRes, medsRes, dosesRes] = await Promise.all([
        api.get(`/patients/${id}`),
        api.get(`/medications/patient/${id}`),
        api.get(`/doses/today/${id}`),
      ]);
      setPatient(patientRes.data);
      setMedications(medsRes.data);
      setTodayDoses(dosesRes.data);
    } catch {
      setPatient(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [id]);

  const handleConfirm = async (logId) => {
    try { await api.post(`/doses/confirm/${logId}`); } catch { /* already handled by interceptor */ }
    load();
  };

  const handleSkip = async (logId) => {
    try { await api.post(`/doses/skip/${logId}`); } catch { /* already handled by interceptor */ }
    load();
  };

  const handleDeleteMed = async (medId) => {
    if (!window.confirm("Remover este medicamento?")) return;
    try { await api.delete(`/medications/${medId}`); } catch { /* already handled by interceptor */ }
    load();
  };

  const handleToggleActive = async (med) => {
    try { await api.put(`/medications/${med.id}`, { active: !med.active }); } catch { /* already handled by interceptor */ }
    load();
  };

  if (loading) return <div className="loading-msg">Carregando...</div>;
  if (!patient) return <div className="loading-msg">Paciente não encontrado</div>;

  const pending = todayDoses.filter(d => d.status === "pending");
  const taken = todayDoses.filter(d => d.status === "taken");
  const missed = todayDoses.filter(d => d.status === "missed");

  return (
    <div className="patient-detail">
      <div className="detail-header">
        <div className="detail-breadcrumb">
          <Link to="/">Pacientes</Link>
          <span> / </span>
          <span>{patient.name}</span>
        </div>
        <div className="detail-title-row">
          <div className="patient-avatar-lg">{patient.name.charAt(0)}</div>
          <div>
            <h1>{patient.name}</h1>
            {patient.notes && <p className="detail-notes">{patient.notes}</p>}
          </div>
        </div>
      </div>

      <div className="detail-stats-bar">
        <div className="stat-badge stat-pending">{pending.length} pendentes</div>
        <div className="stat-badge stat-taken">{taken.length} tomadas</div>
        <div className="stat-badge stat-missed">{missed.length} perdidas</div>
      </div>

      <div className="detail-tabs">
        <button
          className={`tab-btn ${tab === "hoje" ? "active" : ""}`}
          onClick={() => setTab("hoje")}
        >
          Doses de hoje
        </button>
        <button
          className={`tab-btn ${tab === "meds" ? "active" : ""}`}
          onClick={() => setTab("meds")}
        >
          Medicamentos ({medications.length})
        </button>
        <Link to={`/paciente/${id}/historico`} className="tab-btn">
          Histórico
        </Link>
      </div>

      {tab === "hoje" && (
        <div className="doses-section">
          {todayDoses.length === 0 ? (
            <div className="empty-state" style={{ padding: "40px 0" }}>
              <span className="empty-icon">✅</span>
              <p>Nenhuma dose programada para hoje.</p>
            </div>
          ) : (
            <div className="doses-list">
              {todayDoses.map(dose => (
                <DoseCard
                  key={dose.id}
                  dose={dose}
                  onConfirm={() => handleConfirm(dose.id)}
                  onSkip={() => handleSkip(dose.id)}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {tab === "meds" && (
        <div className="meds-section">
          <div className="section-header">
            <h2>Medicamentos cadastrados</h2>
            <button className="btn-primary btn-sm" onClick={() => setShowMedModal(true)}>
              + Adicionar
            </button>
          </div>
          {medications.length === 0 ? (
            <div className="empty-state" style={{ padding: "40px 0" }}>
              <span className="empty-icon">💊</span>
              <p>Nenhum medicamento cadastrado.</p>
              <button className="btn-primary" onClick={() => setShowMedModal(true)}>
                Adicionar medicamento
              </button>
            </div>
          ) : (
            <div className="med-list">
              {medications.map(med => (
                <div key={med.id} className={`med-item ${!med.active ? "inactive" : ""}`}>
                  <div className="med-item-main">
                    <div className="med-pill">💊</div>
                    <div className="med-info">
                      <h3>{med.name}</h3>
                      <p>{med.dose} — {med.frequency}</p>
                      <p className="med-times">{med.schedule_times.join(", ")}</p>
                      {med.stock_quantity !== null && (
                        <p className={`med-stock ${med.stock_quantity <= med.stock_alert_at ? "low" : ""}`}>
                          Estoque: {med.stock_quantity} un.
                          {med.stock_quantity <= med.stock_alert_at && " ⚠️ Baixo"}
                        </p>
                      )}
                      {med.instructions && <p className="med-instructions">{med.instructions}</p>}
                    </div>
                    {!med.active && <span className="badge-inactive">Inativo</span>}
                  </div>
                  <div className="med-actions">
                    <button
                      className="btn-outline btn-sm"
                      onClick={() => { setEditMed(med); setShowMedModal(true); }}
                    >
                      Editar
                    </button>
                    <button
                      className="btn-outline btn-sm"
                      onClick={() => handleToggleActive(med)}
                    >
                      {med.active ? "Pausar" : "Reativar"}
                    </button>
                    <button className="btn-danger btn-sm" onClick={() => handleDeleteMed(med.id)}>
                      Remover
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {showMedModal && (
        <MedicationModal
          patientId={parseInt(id)}
          medication={editMed}
          onClose={() => { setShowMedModal(false); setEditMed(null); }}
          onSaved={() => { setShowMedModal(false); setEditMed(null); load(); }}
        />
      )}
    </div>
  );
}
