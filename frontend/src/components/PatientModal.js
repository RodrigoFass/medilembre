import React, { useState } from "react";
import ReactDOM from "react-dom";
import api from "../services/api";
import "./Modal.css";

export default function PatientModal({ patient, onClose, onSaved }) {
  const [form, setForm] = useState({
    name: patient?.name || "",
    birth_date: patient?.birth_date || "",
    notes: patient?.notes || "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const submit = async e => {
    e.preventDefault();
    setLoading(true);
    setError("");
    const payload = {
      ...form,
      birth_date: form.birth_date || null,
    };
    try {
      if (patient) {
        await api.put(`/patients/${patient.id}`, payload);
      } else {
        await api.post("/patients/", payload);
      }
      onSaved();
    } catch (err) {
      setError(err.response?.data?.error || "Erro ao salvar");
    } finally {
      setLoading(false);
    }
  };

  const modal = (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="ml-modal">
        <div className="ml-modal-header">
          <h2>{patient ? "Editar paciente" : "Novo paciente"}</h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <form onSubmit={submit} className="ml-modal-form">
          <div className="field">
            <label>Nome completo *</label>
            <input
              type="text"
              value={form.name}
              onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
              placeholder="Ex: Maria Silva"
              required
            />
          </div>
          <div className="field">
            <label>Data de nascimento</label>
            <input
              type="date"
              value={form.birth_date}
              onChange={e => setForm(f => ({ ...f, birth_date: e.target.value }))}
            />
          </div>
          <div className="field">
            <label>Observações</label>
            <textarea
              value={form.notes}
              onChange={e => setForm(f => ({ ...f, notes: e.target.value }))}
              placeholder="Condições, alergias, observações relevantes..."
              rows={3}
            />
          </div>
          {error && <div className="error-msg">{error}</div>}
          <div className="ml-modal-footer">
            <button type="button" className="btn-outline" onClick={onClose}>Cancelar</button>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? "Salvando..." : "Salvar"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );

  return ReactDOM.createPortal(modal, document.body);
}
