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
                padding-top: 3rem !important;
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

            [data-testid="stSidebar"] h3 {{
                font-size: 1rem !important;
                font-weight: 760 !important;
                margin-bottom: 1.2rem !important;
            }}

            [data-testid="stPageLink"] a {{
                border-radius: 8px !important;
                min-height: 2.25rem !important;
            }}

            [data-testid="stVerticalBlockBorderWrapper"] {{
                border: 1px solid var(--kw-border) !important;
                border-radius: 8px !important;
                background: linear-gradient(180deg, rgba(255,255,255,0.035), rgba(255,255,255,0.012)) !important;
                padding: 1.15rem !important;
            }}

            div[data-baseweb="select"] > div {{
                min-height: 3.15rem !important;
                border-radius: 8px !important;
                border-color: rgba(148, 163, 184, 0.22) !important;
                background: var(--kw-surface-soft) !important;
            }}

            div[data-baseweb="select"] > div:hover {{
                border-color: rgba(148, 163, 184, 0.38) !important;
            }}

            div[data-baseweb="select"] span {{
                font-weight: 540 !important;
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
                font-size: clamp(2.2rem, 3.2vw, 3.35rem);
                line-height: 1.02;
                font-weight: 760;
                margin: 0;
                max-width: 820px;
            }}

            .kw-subtitle {{
                color: var(--kw-muted);
                font-size: 1.05rem;
                line-height: 1.7;
                max-width: 760px;
                margin-top: 0.85rem;
                margin-bottom: 0;
            }}

            .kw-start-note {{
                color: var(--kw-muted);
                font-size: 0.86rem;
                line-height: 1.55;
                margin-top: 0.85rem;
                max-width: 60ch;
            }}

            .kw-command-brief {{
                border: 1px solid rgba(37, 99, 235, 0.34);
                border-radius: 8px;
                background:
                    linear-gradient(135deg, rgba(37, 99, 235, 0.12), rgba(255,255,255,0.018) 38%, rgba(255,255,255,0.01)),
                    linear-gradient(180deg, rgba(255,255,255,0.035), rgba(255,255,255,0.012));
                padding: 1.4rem;
                margin: 1.45rem 0 1.2rem 0;
            }}

            .kw-command-grid {{
                display: grid;
                grid-template-columns: minmax(0, 1.35fr) minmax(260px, 0.75fr);
                gap: 1.4rem;
                align-items: end;
            }}

            .kw-command-copy {{
                color: var(--kw-soft);
                font-size: 1rem;
                line-height: 1.65;
                max-width: 72ch;
                margin: 0.7rem 0 0 0;
            }}

            .kw-route {{
                display: flex;
                flex-wrap: wrap;
                gap: 0.45rem;
                justify-content: flex-end;
            }}

            .kw-route-step {{
                border: 1px solid var(--kw-border);
                border-radius: 999px;
                color: var(--kw-muted);
                font-size: 0.78rem;
                font-weight: 650;
                padding: 0.36rem 0.62rem;
                white-space: nowrap;
            }}

            .kw-route-step-active {{
                color: var(--kw-text);
                background: rgba(37, 99, 235, 0.16);
                border-color: rgba(37, 99, 235, 0.62);
            }}

            .kw-panel-kicker {{
                color: var(--kw-accent);
                font-size: 0.74rem;
                font-weight: 760;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                margin-bottom: 0.85rem;
            }}

            .kw-evidence-list {{
                display: grid;
                gap: 0.8rem;
                margin-top: 1.15rem;
            }}

            .kw-evidence-item {{
                border-top: 1px solid var(--kw-border);
                padding-top: 0.8rem;
            }}

            .kw-evidence-item strong {{
                color: var(--kw-text);
                display: block;
                font-size: 0.92rem;
                font-weight: 720;
                margin-bottom: 0.2rem;
            }}

            .kw-evidence-item span {{
                color: var(--kw-muted);
                display: block;
                font-size: 0.86rem;
                line-height: 1.5;
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
                gap: 1.15rem;
                margin-top: 0.95rem;
            }}

            .kw-stat {{
                display: inline-flex;
                flex-direction: column;
                gap: 0.16rem;
                align-items: flex-start;
                color: var(--kw-muted);
                font-size: 0.86rem;
            }}

            .kw-stat strong {{
                color: var(--kw-text);
                font-size: 0.9rem;
                font-weight: 760;
            }}

            @media (max-width: 760px) {{
                .block-container {{
                    padding-left: 1rem !important;
                    padding-right: 1rem !important;
                    padding-top: 1.5rem !important;
                }}

                .kw-command-grid {{
                    grid-template-columns: 1fr;
                }}

                .kw-route {{
                    justify-content: flex-start;
                }}
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


def command_brief(title: str, copy: str, steps: Iterable[str], active_step: str) -> None:
    step_html = "".join(
        (
            f"<span class='kw-route-step kw-route-step-active'>{_escape(step)}</span>"
            if step == active_step
            else f"<span class='kw-route-step'>{_escape(step)}</span>"
        )
        for step in steps
    )
    st.markdown(
        f"""
        <div class="kw-command-brief">
            <div class="kw-eyebrow">Career intelligence</div>
            <div class="kw-command-grid">
                <div>
                    <h1 class="kw-title">{_escape(title)}</h1>
                    <p class="kw-command-copy">{_escape(copy)}</p>
                </div>
                <div class="kw-route">{step_html}</div>
            </div>
        </div>
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


def start_note(message: str) -> None:
    st.markdown(
        f"<p class='kw-start-note'>{_escape(message)}</p>",
        unsafe_allow_html=True,
    )


def evidence_brief(items: Iterable[tuple[str, str]]) -> None:
    rows = "".join(
        f"<div class='kw-evidence-item'><strong>{_escape(title)}</strong><span>{_escape(copy)}</span></div>"
        for title, copy in items
    )
    st.markdown(
        f"""
        <div class="kw-panel-kicker">What happens next</div>
        <div class="kw-evidence-list">{rows}</div>
        """,
        unsafe_allow_html=True,
    )


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
