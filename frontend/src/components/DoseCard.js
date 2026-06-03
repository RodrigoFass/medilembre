import React from "react";
import "./DoseCard.css";

const STATUS_LABELS = { pending: "Pendente", taken: "Tomado", missed: "Perdido" };

// Backend stores naive local datetimes without "Z". Appending "Z" would
// wrongly treat them as UTC. We parse manually to preserve local display.
function parseLocalDateTime(str) {
  if (!str) return null;
  // "2024-01-01T08:00:00" → treat as local, not UTC
  const [datePart, timePart = "00:00:00"] = str.split("T");
  const [y, mo, d] = datePart.split("-").map(Number);
  const [h, mi] = timePart.split(":").map(Number);
  return new Date(y, mo - 1, d, h, mi);
}

export default function DoseCard({ dose, onConfirm, onSkip }) {
  const scheduled = parseLocalDateTime(dose.scheduled_time);
  const takenAt = parseLocalDateTime(dose.taken_at);

  const time = scheduled
    ? scheduled.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })
    : "--:--";

  return (
    <div className={`dose-card dose-${dose.status}`}>
      <div className="dose-time">{time}</div>
      <div className="dose-info">
        <span className="dose-name">{dose.medication_name}</span>
        {dose.dose && <span className="dose-amount">{dose.dose}</span>}
        <span className={`dose-badge dose-badge-${dose.status}`}>
          {STATUS_LABELS[dose.status]}
        </span>
      </div>
      {dose.status === "pending" && (
        <div className="dose-actions">
          <button className="btn-confirm" onClick={onConfirm}>✓ Tomei</button>
          <button className="btn-skip" onClick={onSkip}>✗ Pular</button>
        </div>
      )}
      {dose.status === "taken" && takenAt && (
        <div className="dose-taken-info">
          Às {takenAt.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}
        </div>
      )}
    </div>
  );
}
