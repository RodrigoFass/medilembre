import React, { useState } from "react";
import ReactDOM from "react-dom";
import api from "../services/api";
import "./Modal.css";

const FREQUENCIES = [
  { value: "1x ao dia", label: "1x ao dia" },
  { value: "2x ao dia", label: "2x ao dia" },
  { value: "3x ao dia", label: "3x ao dia" },
  { value: "4x ao dia", label: "4x ao dia" },
  { value: "A cada 8 horas", label: "A cada 8 horas" },
  { value: "A cada 12 horas", label: "A cada 12 horas" },
  { value: "Quando necessário", label: "Quando necessário" },
];

export default function MedicationModal({ patientId, medication, onClose, onSaved }) {
  const timesCount = medication ? JSON.parse(
    typeof medication.schedule_times === "string"
      ? medication.schedule_times
      : JSON.stringify(medication.schedule_times)
  ).length : 1;

  const [form, setForm] = useState({
    name: medication?.name || "",
    dose: medication?.dose || "",
    frequency: medication?.frequency || "1x ao dia",
    schedule_times: medication?.schedule_times || ["08:00"],
    start_date: medication?.start_date || new Date().toISOString().split("T")[0],
    end_date: medication?.end_date || "",
    stock_quantity: medication?.stock_quantity ?? "",
    stock_alert_at: medication?.stock_alert_at ?? 5,
    instructions: medication?.instructions || "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const updateTime = (index, value) => {
    setForm(f => {
      const times = [...f.schedule_times];
      times[index] = value;
      return { ...f, schedule_times: times };
    });
  };

  const setTimesCount = (n) => {
    setForm(f => {
      const current = f.schedule_times;
      const next = Array.from({ length: n }, (_, i) => current[i] || "08:00");
      return { ...f, schedule_times: next };
    });
  };

  const submit = async e => {
    e.preventDefault();
    setLoading(true);
    setError("");
    const payload = {
      ...form,
      stock_quantity: form.stock_quantity === "" ? null : parseInt(form.stock_quantity),
      stock_alert_at: parseInt(form.stock_alert_at),
      end_date: form.end_date || null,
    };
    try {
      if (medication) {
        await api.put(`/medications/${medication.id}`, payload);
      } else {
        await api.post(`/medications/patient/${patientId}`, payload);
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
          <h2>{medication ? "Editar medicamento" : "Novo medicamento"}</h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <form onSubmit={submit} className="ml-modal-form">
          <div className="field">
            <label>Nome do medicamento *</label>
            <input
              type="text"
              value={form.name}
              onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
              placeholder="Ex: Losartana 50mg"
              required
            />
          </div>
          <div className="form-row">
            <div className="field">
              <label>Dose *</label>
              <input
                type="text"
                value={form.dose}
                onChange={e => setForm(f => ({ ...f, dose: e.target.value }))}
                placeholder="Ex: 1 comprimido"
                required
              />
            </div>
            <div className="field">
              <label>Frequência *</label>
              <select
                value={form.frequency}
                onChange={e => {
                  const freq = e.target.value;
                  const counts = { "1x ao dia": 1, "2x ao dia": 2, "3x ao dia": 3, "4x ao dia": 4,
                    "A cada 8 horas": 3, "A cada 12 horas": 2, "Quando necessário": 1 };
                  setForm(f => ({ ...f, frequency: freq }));
                  setTimesCount(counts[freq] || 1);
                }}
              >
                {FREQUENCIES.map(f => <option key={f.value} value={f.value}>{f.label}</option>)}
              </select>
            </div>
          </div>

          <div className="field">
            <label>Horários *</label>
            <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
              {form.schedule_times.map((t, i) => (
                <input
                  key={i}
                  type="time"
                  value={t}
                  onChange={e => updateTime(i, e.target.value)}
                  style={{ width: "130px" }}
                  required
                />
              ))}
            </div>
          </div>

          <div className="form-row">
            <div className="field">
              <label>Data de início *</label>
              <input
                type="date"
                value={form.start_date}
                onChange={e => setForm(f => ({ ...f, start_date: e.target.value }))}
                required
              />
            </div>
            <div className="field">
              <label>Data de término</label>
              <input
                type="date"
                value={form.end_date}
                onChange={e => setForm(f => ({ ...f, end_date: e.target.value }))}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="field">
              <label>Estoque (unidades)</label>
              <input
                type="number"
                min="0"
                value={form.stock_quantity}
                onChange={e => setForm(f => ({ ...f, stock_quantity: e.target.value }))}
                placeholder="Deixe vazio para não controlar"
              />
            </div>
            <div className="field">
              <label>Alertar com menos de</label>
              <input
                type="number"
                min="1"
                value={form.stock_alert_at}
                onChange={e => setForm(f => ({ ...f, stock_alert_at: e.target.value }))}
              />
            </div>
          </div>

          <div className="field">
            <label>Instruções / observações</label>
            <textarea
              value={form.instructions}
              onChange={e => setForm(f => ({ ...f, instructions: e.target.value }))}
              placeholder="Ex: Tomar com água, após as refeições..."
              rows={2}
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
