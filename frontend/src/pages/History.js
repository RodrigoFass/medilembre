import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import api from "../services/api";
import "./History.css";

function parseLocalDateTime(str) {
  if (!str) return null;
  const [datePart, timePart = "00:00:00"] = str.split("T");
  const [y, mo, d] = datePart.split("-").map(Number);
  const [h, mi] = timePart.split(":").map(Number);
  return new Date(y, mo - 1, d, h, mi);
}

function AdherenceRing({ percent }) {
  const r = 40;
  const circ = 2 * Math.PI * r;
  const offset = circ - (percent / 100) * circ;
  return (
    <div className="adherence-circle">
      <svg className="adherence-ring" viewBox="0 0 100 100">
        <circle className="adherence-ring-bg" cx="50" cy="50" r={r} />
        <circle
          className="adherence-ring-fill"
          cx="50"
          cy="50"
          r={r}
          style={{ strokeDasharray: circ, strokeDashoffset: offset }}
        />
      </svg>
      <div className="adherence-center">
        <span className="adherence-value">{percent}%</span>
        <span className="adherence-label">de adesão</span>
      </div>
    </div>
  );
}

export default function History() {
  const { id } = useParams();
  const [patient, setPatient] = useState(null);
  const [data, setData] = useState(null);
  const [days, setDays] = useState(30);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const [patientRes, histRes] = await Promise.all([
        api.get(`/patients/${id}`),
        api.get(`/doses/history/${id}?days=${days}`),
      ]);
      setPatient(patientRes.data);
      setData(histRes.data);
    } catch {
      setData({ logs: [], summary: {} });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [id, days]);

  const exportPdf = async () => {
    setExporting(true);
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(
        `${process.env.REACT_APP_API_URL || "http://localhost:5000/api"}/reports/pdf/${id}?days=${days}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `medilembre_historico.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } finally {
      setExporting(false);
    }
  };

  if (loading) return <div className="loading-msg">Carregando histórico...</div>;

  const { logs, summary } = data || { logs: [], summary: {} };
  const adherence = summary.adherence_percent ?? 0;

  return (
    <div className="history-page">
      <div className="detail-breadcrumb" style={{ marginBottom: 20 }}>
        <Link to="/">Pacientes</Link>
        <span>/</span>
        <Link to={`/paciente/${id}`}>{patient?.name}</Link>
        <span>/</span>
        <span>Histórico</span>
      </div>

      <div className="history-header">
        <h1>Histórico de adesão</h1>
        <div className="history-controls">
          <select value={days} onChange={e => setDays(Number(e.target.value))}>
            <option value={7}>Últimos 7 dias</option>
            <option value={15}>Últimos 15 dias</option>
            <option value={30}>Últimos 30 dias</option>
            <option value={60}>Últimos 60 dias</option>
            <option value={90}>Últimos 90 dias</option>
          </select>
          <button className="btn-primary btn-sm" onClick={exportPdf} disabled={exporting}>
            {exporting ? "Gerando…" : "⬇ Exportar PDF"}
          </button>
        </div>
      </div>

      <div className="adherence-card">
        <AdherenceRing percent={adherence} />
        <div className="adherence-stats">
          <div className="adh-stat">
            <span className="adh-num">{summary.total ?? 0}</span>
            <span className="adh-desc">Total de doses</span>
          </div>
          <div className="adh-stat taken">
            <span className="adh-num">{summary.taken ?? 0}</span>
            <span className="adh-desc">Tomadas</span>
          </div>
          <div className="adh-stat missed">
            <span className="adh-num">{summary.missed ?? 0}</span>
            <span className="adh-desc">Perdidas</span>
          </div>
          <div className="adh-stat pending">
            <span className="adh-num">{summary.pending ?? 0}</span>
            <span className="adh-desc">Pendentes</span>
          </div>
        </div>
      </div>

      <h2 className="history-section-title">Detalhamento</h2>

      {logs.length === 0 ? (
        <div className="empty-state">
          <span className="empty-icon">📋</span>
          <h2>Sem registros</h2>
          <p>Nenhum registro neste período.</p>
        </div>
      ) : (
        <div className="history-table-wrap">
          <table className="history-table">
            <thead>
              <tr>
                <th>Medicamento</th>
                <th>Horário programado</th>
                <th>Tomado às</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {logs.map(log => (
                <tr key={log.id} className={`row-${log.status}`}>
                  <td>{log.medication_name}</td>
                  <td>{parseLocalDateTime(log.scheduled_time)?.toLocaleString("pt-BR", {
                    day: "2-digit", month: "2-digit", year: "numeric",
                    hour: "2-digit", minute: "2-digit"
                  }) ?? "—"}</td>
                  <td>{log.taken_at
                    ? parseLocalDateTime(log.taken_at)?.toLocaleTimeString("pt-BR", {
                        hour: "2-digit", minute: "2-digit"
                      })
                    : "—"
                  }</td>
                  <td>
                    <span className={`dose-badge dose-badge-${log.status}`}>
                      {{ taken: "Tomado", missed: "Perdido", pending: "Pendente" }[log.status]}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
