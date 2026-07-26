"""Jupyter display helpers for the Phishing Email Triage Agent labs.

Provides color-coded verdicts, formatted tables, and graph visualization
helpers for use in notebook cells.
"""

from IPython.display import display, HTML, Markdown


# ---------------------------------------------------------------------------
# Verdict display
# ---------------------------------------------------------------------------

_VERDICT_COLORS = {
    "phishing": "#e74c3c",     # red
    "suspicious": "#f39c12",   # orange
    "legitimate": "#27ae60",   # green
}

_VERDICT_EMOJI = {
    "phishing": "&#x1F6A8;",
    "suspicious": "&#x26A0;&#xFE0F;",
    "legitimate": "&#x2705;",
}

_CONFIDENCE_BAR_WIDTH = 200


def display_verdict(email_id: str, verdict: str, confidence: float, reasoning: str = ""):
    """Display a color-coded verdict card for an email.

    Args:
        email_id: The email ID (e.g., "EMAIL-001").
        verdict: Classification result ("phishing", "suspicious", or "legitimate").
        confidence: Confidence score between 0 and 1.
        reasoning: Optional short explanation.
    """
    verdict_lower = verdict.lower()
    color = _VERDICT_COLORS.get(verdict_lower, "#95a5a6")
    emoji = _VERDICT_EMOJI.get(verdict_lower, "")
    bar_fill = int(confidence * _CONFIDENCE_BAR_WIDTH)

    html = f"""
    <div style="border: 2px solid {color}; border-radius: 8px; padding: 12px; margin: 8px 0;
                background-color: {color}11; font-family: sans-serif;">
        <div style="font-size: 14px; font-weight: bold; color: #333;">
            {emoji} {email_id}
        </div>
        <div style="font-size: 20px; font-weight: bold; color: {color}; margin: 4px 0;">
            {verdict.upper()}
        </div>
        <div style="margin: 4px 0;">
            <span style="font-size: 12px; color: #666;">Confidence:</span>
            <div style="background: #eee; border-radius: 4px; width: {_CONFIDENCE_BAR_WIDTH}px;
                        height: 12px; display: inline-block; vertical-align: middle;">
                <div style="background: {color}; border-radius: 4px; width: {bar_fill}px;
                            height: 12px;"></div>
            </div>
            <span style="font-size: 12px; color: #666; margin-left: 4px;">{confidence:.0%}</span>
        </div>
        {"<div style='font-size: 12px; color: #555; margin-top: 6px;'>" + reasoning + "</div>" if reasoning else ""}
    </div>
    """
    display(HTML(html))


def display_batch_results(results: list[dict]):
    """Display a summary table of batch classification results.

    Args:
        results: List of dicts with keys: email_id, verdict, confidence, ground_truth (optional).
    """
    rows = []
    for r in results:
        verdict_lower = r["verdict"].lower()
        color = _VERDICT_COLORS.get(verdict_lower, "#95a5a6")
        gt = r.get("ground_truth", "")
        match = ""
        if gt:
            match = "&#x2705;" if verdict_lower == gt.lower() else "&#x274C;"
        rows.append(
            f"<tr>"
            f"<td style='padding: 6px;'>{r['email_id']}</td>"
            f"<td style='padding: 6px; color: {color}; font-weight: bold;'>{r['verdict'].upper()}</td>"
            f"<td style='padding: 6px;'>{r.get('confidence', 0):.0%}</td>"
            f"<td style='padding: 6px;'>{gt}</td>"
            f"<td style='padding: 6px; text-align: center;'>{match}</td>"
            f"</tr>"
        )

    html = f"""
    <table style="border-collapse: collapse; font-family: sans-serif; font-size: 13px; width: 100%;">
        <thead>
            <tr style="background: #f8f9fa; border-bottom: 2px solid #dee2e6;">
                <th style="padding: 8px; text-align: left;">Email ID</th>
                <th style="padding: 8px; text-align: left;">Verdict</th>
                <th style="padding: 8px; text-align: left;">Confidence</th>
                <th style="padding: 8px; text-align: left;">Ground Truth</th>
                <th style="padding: 8px; text-align: center;">Match</th>
            </tr>
        </thead>
        <tbody>
            {"".join(rows)}
        </tbody>
    </table>
    """
    display(HTML(html))

    # Accuracy summary
    if any(r.get("ground_truth") for r in results):
        correct = sum(
            1 for r in results
            if r.get("ground_truth") and r["verdict"].lower() == r["ground_truth"].lower()
        )
        total = sum(1 for r in results if r.get("ground_truth"))
        display(HTML(
            f"<div style='margin-top: 8px; font-family: sans-serif; font-size: 14px;'>"
            f"<b>Accuracy: {correct}/{total} ({correct/total:.0%})</b></div>"
        ))


def display_investigation_report(report: dict):
    """Display a formatted investigation report.

    Args:
        report: Dict with keys like email_id, verdict, confidence, risk_level,
                evidence (list of strings), recommendation.
    """
    verdict_lower = report.get("verdict", "").lower()
    color = _VERDICT_COLORS.get(verdict_lower, "#95a5a6")
    risk = report.get("risk_level", "unknown").upper()

    evidence_html = ""
    if report.get("evidence"):
        items = "".join(f"<li>{e}</li>" for e in report["evidence"])
        evidence_html = f"<ul style='margin: 4px 0;'>{items}</ul>"

    html = f"""
    <div style="border: 2px solid {color}; border-radius: 8px; padding: 16px; margin: 8px 0;
                background-color: {color}11; font-family: sans-serif;">
        <div style="font-size: 16px; font-weight: bold; color: #333; border-bottom: 1px solid #ddd;
                    padding-bottom: 8px; margin-bottom: 8px;">
            Investigation Report: {report.get('email_id', 'N/A')}
        </div>
        <table style="font-size: 13px; margin-bottom: 8px;">
            <tr><td style="padding: 2px 12px 2px 0; font-weight: bold;">Verdict:</td>
                <td style="color: {color}; font-weight: bold;">{report.get('verdict', 'N/A').upper()}</td></tr>
            <tr><td style="padding: 2px 12px 2px 0; font-weight: bold;">Confidence:</td>
                <td>{report.get('confidence', 0):.0%}</td></tr>
            <tr><td style="padding: 2px 12px 2px 0; font-weight: bold;">Risk Level:</td>
                <td>{risk}</td></tr>
        </table>
        {"<div style='font-size: 13px;'><b>Evidence:</b>" + evidence_html + "</div>" if evidence_html else ""}
        {"<div style='font-size: 13px; margin-top: 4px;'><b>Recommendation:</b> " + report.get('recommendation', '') + "</div>" if report.get('recommendation') else ""}
    </div>
    """
    display(HTML(html))


def display_graph_mermaid(graph, title: str = "Agent Graph"):
    """Render a LangGraph graph's Mermaid diagram in Jupyter.

    Args:
        graph: A compiled LangGraph StateGraph.
        title: Optional title for the diagram.
    """
    try:
        mermaid_png = graph.get_graph().draw_mermaid_png()
        from IPython.display import Image
        display(Markdown(f"### {title}"))
        display(Image(mermaid_png))
    except Exception as e:
        # Fallback: display Mermaid text
        try:
            mermaid_text = graph.get_graph().draw_mermaid()
            display(Markdown(f"### {title}\n```mermaid\n{mermaid_text}\n```"))
        except Exception:
            display(Markdown(f"*Could not render graph: {e}*"))
