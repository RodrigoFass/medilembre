from flask import Blueprint, send_file, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import re
from app.models.patient import Patient
from app.models.dose_log import DoseLog
from app.models.medication import Medication
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
import io

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/pdf/<int:patient_id>", methods=["GET"])
@jwt_required()
def generate_pdf(patient_id):
    uid = int(get_jwt_identity())
    patient = Patient.query.filter_by(id=patient_id, user_id=uid).first_or_404()

    try:
        days = max(1, min(int(request.args.get("days", 30)), 365))
    except (ValueError, TypeError):
        days = 30
    since = datetime.utcnow() - timedelta(days=days)

    logs = (
        DoseLog.query
        .join(Medication)
        .filter(
            Medication.patient_id == patient_id,
            DoseLog.scheduled_time >= since,
        )
        .order_by(DoseLog.scheduled_time)
        .all()
    )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    orange = colors.HexColor("#E07B39")

    title_style = ParagraphStyle("title", parent=styles["Title"], textColor=orange, fontSize=20)
    subtitle_style = ParagraphStyle("sub", parent=styles["Normal"], fontSize=11, textColor=colors.grey)

    elements = []
    elements.append(Paragraph("MediLembre", title_style))
    elements.append(Paragraph(f"Relatório de Adesão ao Tratamento", subtitle_style))
    elements.append(Spacer(1, 0.4*cm))
    elements.append(Paragraph(f"Paciente: {patient.name}", styles["Normal"]))
    elements.append(Paragraph(f"Período: últimos {days} dias", styles["Normal"]))
    elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles["Normal"]))
    elements.append(Spacer(1, 0.6*cm))

    total = len(logs)
    taken = sum(1 for l in logs if l.status == "taken")
    missed = sum(1 for l in logs if l.status == "missed")
    adherence = round((taken / total * 100) if total > 0 else 0, 1)

    summary_data = [
        ["Total de doses", "Tomadas", "Perdidas", "Pendentes", "Adesão"],
        [str(total), str(taken), str(missed), str(total - taken - missed), f"{adherence}%"],
    ]
    summary_table = Table(summary_data, colWidths=[3.2*cm]*5)
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), orange),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.6*cm))

    elements.append(Paragraph("Detalhamento das Doses", ParagraphStyle(
        "h2", parent=styles["Heading2"], textColor=orange)))
    elements.append(Spacer(1, 0.3*cm))

    table_data = [["Medicamento", "Horário Programado", "Tomado às", "Status"]]
    status_map = {"taken": "Tomado", "missed": "Perdido", "pending": "Pendente"}
    for log in logs:
        table_data.append([
            log.medication.name,
            log.scheduled_time.strftime("%d/%m/%Y %H:%M"),
            log.taken_at.strftime("%d/%m/%Y %H:%M") if log.taken_at else "-",
            status_map.get(log.status, log.status),
        ])

    detail_table = Table(table_data, colWidths=[5*cm, 4*cm, 4*cm, 3*cm])
    detail_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), orange),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
    ]))
    elements.append(detail_table)

    doc.build(elements)
    buffer.seek(0)
    return send_file(buffer, mimetype="application/pdf",
                     download_name=f"medilembre_{re.sub(r'[^a-zA-Z0-9_-]', '_', patient.name)}_{datetime.now().strftime('%Y%m%d')}.pdf")
