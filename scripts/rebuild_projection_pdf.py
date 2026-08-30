#!/usr/bin/env python3
"""Rebuild a simple script PDF into a high-contrast projection-friendly version."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, KeepTogether


OUTPUT = Path("/Users/a14/Downloads/Databricks_Presentation_Script_High_Contrast.pdf")


TITLE = "Databricks Presentation Script"
SUBTITLE = "Marcelo Zapata  |  June 11, 2026  |  1:00 - 2:00 PM"


SECTIONS = [
    (
        "INTRO (~30 sec)",
        [
            "Hey everyone - I'll cover what Databricks is, why we use it, and how we use it in practice.",
            "Then Raghu will do a live walkthrough, and I'll close with how this connects to the business.",
        ],
    ),
    (
        "WHAT IS DATABRICKS (~2 min)",
        [
            "Databricks is a cloud platform where we write and run SQL and Python to work with large amounts of data.",
            "In our case, it connects to our Azure Data Lake.",
        ],
    ),
    (
        "WHY WE USE IT (~2 min)",
        [
            "We use it because it gives us one unified place to query, transform, and validate data from the Data Lake.",
            "That way, when other tools connect to it, the data is already clean and structured.",
        ],
    ),
    (
        "HOW WE USE IT - Live Repo (~5 min)",
        [
            "[SHARE SCREEN - open WISR repo: S0WISRXX / WISR-DSCSA-Datalake]",
            "Let me show you what that looks like in practice. This is one of our project repos in Azure DevOps. Inside you'll see two key pieces.",
            "[Point to: Wisr_Extracts_Wrapper]",
            "First - the extract wrapper. This notebook pulls data from the source system and lands it in Azure Data Lake Storage in a consistent, repeatable way.",
            "Instead of every job doing it differently, the wrapper standardizes the process.",
            "[Point to: DSCSA_DTLK_LOAD.DEV / .PRD / .STG / .TST]",
            "Second - the load notebooks. These pick up the data from the lake and load it into Databricks tables.",
            "We have separate versions for each environment - dev, staging, test, and production.",
            "I'll hand it to Raghu now to show you the actual Databricks workspace.",
        ],
    ),
    (
        "RAGHU'S SECTION (~8 min)",
        [
            "[Hand off to Raghu - Data Lake, Workspace, Cluster, Unity Catalog, Schema & Tables, SQL Editor]",
        ],
    ),
    (
        "CLOSING - Power BI (~2 min)",
        [
            "To wrap up - once data is clean and structured in Databricks, low-code tools like Power BI can connect straight to it.",
            "The business can explore and build dashboards without waiting on our team. That's why data quality and structure at this layer matters.",
        ],
    ),
    (
        "Q&A",
        [
            "Any questions?",
            "If asked something you don't know: Good question - let me follow up on that.",
        ],
    ),
]


def build_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "TitleHC",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=27,
            leading=31,
            textColor=colors.HexColor("#111111"),
            spaceAfter=10,
            alignment=0,
        ),
        "subtitle": ParagraphStyle(
            "SubtitleHC",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=14.5,
            leading=18,
            textColor=colors.HexColor("#2A2A2A"),
            spaceAfter=20,
        ),
        "header": ParagraphStyle(
            "HeaderHC",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#4A250A"),
            spaceBefore=8,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "BodyHC",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=16,
            leading=22,
            textColor=colors.HexColor("#111111"),
            spaceAfter=8,
        ),
        "cue": ParagraphStyle(
            "CueHC",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=15.5,
            leading=20,
            textColor=colors.HexColor("#0B3A5B"),
            backColor=colors.HexColor("#EAF6FF"),
            borderPadding=(6, 6, 6),
            spaceAfter=10,
        ),
    }


def main() -> None:
    styles = build_styles()
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        leftMargin=0.85 * inch,
        rightMargin=0.85 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
    )

    story = [
        Paragraph(TITLE, styles["title"]),
        Paragraph(SUBTITLE, styles["subtitle"]),
        Spacer(1, 0.05 * inch),
    ]

    for heading, bullets in SECTIONS:
        block = [Paragraph(heading, styles["header"])]
        for line in bullets:
            style = styles["cue"] if line.startswith("[") and line.endswith("]") else styles["body"]
            block.append(Paragraph(line, style))
        block.append(Spacer(1, 0.09 * inch))
        story.append(KeepTogether(block))

    doc.build(story)
    print(OUTPUT)


if __name__ == "__main__":
    main()
