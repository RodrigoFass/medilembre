import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";
import PatientModal from "../components/PatientModal";
import "./Dashboard.css";

export default function Dashboard() {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editPatient, setEditPatient] = useState(null);

  const load = async () => {
    try {
      const r = await api.get("/patients/");
      setPatients(r.data);
    } catch {
      setPatients([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const handleDelete = async (id) => {
    if (!window.confirm("Remover este paciente e todos os seus dados?")) return;
    try { await api.delete(`/patients/${id}`); } catch { /* o interceptor já trata o erro */ }
    load();
  };

  const handleSaved = () => {
    setShowModal(false);
    setEditPatient(null);
    load();
  };

  if (loading) return <div className="loading-msg">Carregando...</div>;

  return (
    <div className="dashboard">
      <div className="page-header">
        <div>
          <h1>Pacientes</h1>
          <p className="page-subtitle">Gerencie os medicamentos de cada paciente</p>
        </div>
        <button className="btn-primary" onClick={() => setShowModal(true)}>
          + Novo paciente
        </button>
      </div>

      {patients.length === 0 ? (
        <div className="empty-state">
          <span className="empty-icon">👤</span>
          <h2>Nenhum paciente cadastrado</h2>
          <p>Adicione um paciente para começar a controlar os medicamentos.</p>
          <button className="btn-primary" onClick={() => setShowModal(true)}>
            Adicionar paciente
          </button>
        </div>
      ) : (
        <div className="patients-grid">
          {patients.map(p => (
            <div key={p.id} className="patient-card">
              <div className="patient-card-top">
                <div className="patient-avatar">
                  {p.name.charAt(0).toUpperCase()}
                </div>
                <div className="patient-info">
                  <h3>{p.name}</h3>
                  {p.birth_date && (
                    <p className="patient-meta">
                      {calcAge(p.birth_date)} anos
                    </p>
                  )}
                </div>
              </div>
              <div className="patient-stats">
                <span className="stat">
                  💊 {p.medication_count} medicamento{p.medication_count !== 1 ? "s" : ""}
                </span>
              </div>
              {p.notes && <p className="patient-notes">{p.notes}</p>}
              <div className="patient-actions">
                <Link to={`/paciente/${p.id}`} className="btn-primary btn-sm">
                  Ver medicamentos
                </Link>
                <button
                  className="btn-outline btn-sm"
                  onClick={() => { setEditPatient(p); setShowModal(true); }}
                >
                  Editar
                </button>
                <button
                  className="btn-danger btn-sm"
                  onClick={() => handleDelete(p.id)}
                >
                  Remover
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {showModal && (
        <PatientModal
          patient={editPatient}
          onClose={() => { setShowModal(false); setEditPatient(null); }}
          onSaved={handleSaved}
        />
      )}
    </div>
  );
}

function calcAge(birthDateStr) {
  const today = new Date();
  const birth = new Date(birthDateStr);
  let age = today.getFullYear() - birth.getFullYear();
  const m = today.getMonth() - birth.getMonth();
  if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) age--;
  return age;
}
