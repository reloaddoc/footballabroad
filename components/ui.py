import html
from typing import Iterable

import streamlit as st


ACCENT = "#2563eb"


def inject_kickways_theme() -> None:
    st.markdown(
        f"""
        <style>
            :root {{
                --kw-accent: {ACCENT};
                --kw-bg: #0b0d12;
                --kw-surface: #11141b;
                --kw-surface-soft: #151923;
                --kw-border: rgba(148, 163, 184, 0.20);
                --kw-text: #f8fafc;
                --kw-muted: #94a3b8;
                --kw-soft: #cbd5e1;
            }}

            .block-container {{
                max-width: 1180px !important;
                padding-top: 2.25rem !important;
                padding-left: 2rem !important;
                padding-right: 2rem !important;
                padding-bottom: 4rem !important;
            }}

            [data-testid="stSidebar"] {{
                background: #0f1117;
                border-right: 1px solid var(--kw-border);
            }}

            h1, h2, h3 {{
                letter-spacing: 0 !important;
            }}

            div[data-testid="stMetric"] {{
                background: transparent;
                border: 1px solid var(--kw-border);
                border-radius: 8px;
                padding: 1rem 1.1rem;
            }}

            div[data-testid="stMetric"] label {{
                color: var(--kw-muted) !important;
                font-size: 0.82rem !important;
            }}

            div[data-testid="stButton"] > button,
            div[data-testid="stLinkButton"] > a {{
                border-radius: 8px;
                border: 1px solid var(--kw-border);
                font-weight: 650;
            }}

            div[data-testid="stButton"] > button:hover,
            div[data-testid="stLinkButton"] > a:hover {{
                border-color: rgba(148, 163, 184, 0.36);
            }}

            div[data-testid="stButton"] > button[kind="primary"] {{
                background: var(--kw-accent);
                border-color: var(--kw-accent);
            }}

            .kw-eyebrow {{
                color: var(--kw-accent);
                font-size: 0.78rem;
                font-weight: 750;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                margin-bottom: 0.6rem;
            }}

            .kw-title {{
                color: var(--kw-text);
                font-size: clamp(2.1rem, 4vw, 4rem);
                line-height: 1.02;
                font-weight: 760;
                margin: 0;
            }}

            .kw-subtitle {{
                color: var(--kw-muted);
                font-size: 1.05rem;
                line-height: 1.7;
                max-width: 720px;
                margin-top: 0.85rem;
                margin-bottom: 0;
            }}

            .kw-section-title {{
                color: var(--kw-text);
                font-size: 1.25rem;
                font-weight: 720;
                margin: 0 0 0.25rem 0;
            }}

            .kw-section-copy {{
                color: var(--kw-muted);
                font-size: 0.95rem;
                line-height: 1.55;
                margin: 0 0 1.1rem 0;
            }}

            .kw-card {{
                border: 1px solid var(--kw-border);
                border-radius: 8px;
                background: linear-gradient(180deg, rgba(255,255,255,0.035), rgba(255,255,255,0.015));
                padding: 1.15rem;
                margin-bottom: 1.05rem;
            }}

            .kw-card-primary {{
                border-color: rgba(37, 99, 235, 0.48);
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
            }}

            .kw-card-topline {{
                display: flex;
                justify-content: space-between;
                gap: 1rem;
                align-items: flex-start;
            }}

            .kw-country {{
                color: var(--kw-text);
                font-size: 1.35rem;
                font-weight: 760;
                margin: 0;
            }}

            .kw-league {{
                color: var(--kw-soft);
                font-size: 0.96rem;
                font-weight: 620;
                margin-top: 0.18rem;
            }}

            .kw-evidence {{
                color: var(--kw-muted);
                font-size: 0.92rem;
                line-height: 1.5;
                margin-top: 0.85rem;
            }}

            .kw-stepbar {{
                display: flex;
                gap: 0.5rem;
                flex-wrap: wrap;
                margin: 1.35rem 0 1.75rem 0;
            }}

            .kw-step {{
                color: var(--kw-muted);
                border: 1px solid var(--kw-border);
                border-radius: 999px;
                padding: 0.42rem 0.7rem;
                font-size: 0.82rem;
                font-weight: 650;
            }}

            .kw-step-active {{
                color: white;
                border-color: rgba(37, 99, 235, 0.65);
                background: rgba(37, 99, 235, 0.14);
            }}

            .kw-muted {{
                color: var(--kw-muted);
            }}

            .kw-stat-row {{
                display: flex;
                flex-wrap: wrap;
                gap: 1rem;
                margin-top: 0.95rem;
            }}

            .kw-stat {{
                display: inline-flex;
                gap: 0.4rem;
                align-items: baseline;
                color: var(--kw-muted);
                font-size: 0.86rem;
            }}

            .kw-stat strong {{
                color: var(--kw-text);
                font-size: 0.9rem;
                font-weight: 760;
            }}

            .kw-empty-state {{
                border: 1px solid var(--kw-border);
                border-radius: 8px;
                background: linear-gradient(180deg, rgba(255,255,255,0.035), rgba(255,255,255,0.015));
                padding: 1.15rem;
                color: var(--kw-muted);
                font-size: 0.95rem;
                line-height: 1.55;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _escape(value) -> str:
    return html.escape(str(value))


def product_header(title: str, subtitle: str, eyebrow: str | None = None) -> None:
    eyebrow_html = f"<div class='kw-eyebrow'>{_escape(eyebrow)}</div>" if eyebrow else ""
    st.markdown(
        f"""
        {eyebrow_html}
        <h1 class="kw-title">{_escape(title)}</h1>
        <p class="kw-subtitle">{_escape(subtitle)}</p>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, copy: str | None = None) -> None:
    copy_html = f"<p class='kw-section-copy'>{_escape(copy)}</p>" if copy else ""
    st.markdown(
        f"""
        <div class="kw-section-title">{_escape(title)}</div>
        {copy_html}
        """,
        unsafe_allow_html=True,
    )


def journey_steps(active: str) -> None:
    steps = ["Profile", "Opportunities", "Destination"]
    parts = []
    for step in steps:
        class_name = "kw-step kw-step-active" if step == active else "kw-step"
        parts.append(f"<span class='{class_name}'>{_escape(step)}</span>")
    st.markdown(f"<div class='kw-stepbar'>{''.join(parts)}</div>", unsafe_allow_html=True)


def stat_row(items: Iterable[tuple[str, str]]) -> None:
    stats = "".join(
        f"<span class='kw-stat'><span>{_escape(label)}</span><strong>{_escape(value)}</strong></span>"
        for label, value in items
    )
    st.markdown(f"<div class='kw-stat-row'>{stats}</div>", unsafe_allow_html=True)


def destination_card_shell(
    country: str,
    league: str,
    evidence: str,
    metrics: Iterable[tuple[str, str]],
    primary: bool = False,
    action_label: str | None = None,
    action_key: str | None = None,
) -> bool:
    class_name = "kw-card kw-card-primary" if primary else "kw-card"
    metric_html = "".join(
        f"<span class='kw-stat'><span>{_escape(label)}</span><strong>{_escape(value)}</strong></span>"
        for label, value in metrics
    )
    with st.container():
        st.markdown(
            f"""
            <div class="{class_name}">
                <div class="kw-card-topline">
                    <div>
                        <p class="kw-country">{_escape(country)}</p>
                        <div class="kw-league">{_escape(league)}</div>
                    </div>
                </div>
                <div class="kw-evidence">{_escape(evidence)}</div>
                <div class="kw-stat-row">{metric_html}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if action_label and action_key:
            return st.button(
                action_label,
                key=action_key,
                use_container_width=False,
                type="primary" if primary else "secondary",
            )
    return False


def empty_state(message: str) -> None:
    st.markdown(
        f"<div class='kw-empty-state'>{_escape(message)}</div>",
        unsafe_allow_html=True,
    )
