#!/usr/bin/env python3
"""Build a higher-contrast presenter copy of the ORCAS meeting notes PDF."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, ListFlowable, ListItem


OUTPUT = Path("/Users/a14/Downloads/ORCAS_QT_Meeting_Notes_High_Contrast.pdf")


def styles():
    sample = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title",
            parent=sample["Title"],
            fontName="Helvetica-Bold",
            fontSize=25,
            leading=30,
            textColor=colors.HexColor("#111111"),
            spaceAfter=8,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=sample["Normal"],
            fontName="Helvetica-Bold",
            fontSize=14.5,
            leading=18,
            textColor=colors.HexColor("#2A2A2A"),
            spaceAfter=20,
        ),
        "header": ParagraphStyle(
            "Header",
            parent=sample["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=17,
            leading=21,
            textColor=colors.HexColor("#4A250A"),
            spaceBefore=8,
            spaceAfter=8,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=sample["BodyText"],
            fontName="Helvetica",
            fontSize=15.5,
            leading=21,
            textColor=colors.HexColor("#111111"),
            spaceAfter=10,
        ),
        "callout": ParagraphStyle(
            "Callout",
            parent=sample["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=20,
            textColor=colors.HexColor("#5A130D"),
            backColor=colors.HexColor("#FFF1E8"),
            borderPadding=7,
            spaceAfter=10,
        ),
        "linefill": ParagraphStyle(
            "Linefill",
            parent=sample["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=20,
            textColor=colors.HexColor("#0B3A5B"),
            backColor=colors.HexColor("#EAF6FF"),
            borderPadding=7,
            spaceAfter=10,
        ),
    }


def build() -> None:
    s = styles()
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        leftMargin=0.85 * inch,
        rightMargin=0.85 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
    )

    agenda_items = [
        "Quick overview — what is changing for the warehouse team",
        "SharePoint 5000 record limit — currently at 3500, need a plan",
        "DEV testing results",
        "Parallel run dates (PRD & DEV)",
        "Go / No-Go date",
        "Confirm who needs to be looped in before go-live",
    ]

    who_items = ["_______________", "_______________", "_______________"]
    blocker_items = [
        "Confirm PRD workspace for 'get item codes' step — talk to Shawn",
        "SharePoint archiving plan",
        "_______________",
    ]

    story = [
        Paragraph("ORCAS & Quarantine Tracker — Go-Live Planning", s["title"]),
        Paragraph("Meeting Notes  |  June 11, 2026  |  2:00 PM", s["subtitle"]),
        Paragraph("PURPOSE", s["header"]),
        Paragraph(
            "Review the ORCAS and Quarantine Tracker integration and align on a plan to go live on PRD without any issues.",
            s["body"],
        ),
        Paragraph("AGENDA", s["header"]),
        ListFlowable(
            [ListItem(Paragraph(item, s["body"])) for item in agenda_items],
            bulletType="1",
            start="1",
            leftIndent=18,
        ),
        Spacer(1, 0.08 * inch),
        Paragraph("DEV TESTING RESULTS", s["header"]),
        Paragraph(
            "Cleared all existing data and loaded 3 months of records — September, October, and part of November.",
            s["body"],
        ),
        Paragraph(
            "Result: Only 1 error — an item code that was fetched did not exist in the database. Everything else copied correctly.",
            s["body"],
        ),
        Paragraph(
            "BLOCKER: The 'get item codes' step is currently pointing to the DEV workspace (Distribution - Regulatory Compliance DEV). Need to confirm PRD workspace name and dataset before go-live. Follow up with Shawn.",
            s["callout"],
        ),
        Paragraph("SHAREPOINT RECORD LIMIT", s["header"]),
        Paragraph("Current limit: 5,000 records", s["body"]),
        Paragraph("Current count: ~3,500 records", s["body"]),
        Paragraph("Action needed: Decide on archiving strategy or migration plan before hitting the limit.", s["callout"]),
        Paragraph("PARALLEL RUN DATES", s["header"]),
        Paragraph("PRD Start Date: _______________", s["linefill"]),
        Paragraph("DEV End Date: _______________", s["linefill"]),
        Paragraph("Go / No-Go Date: _______________", s["linefill"]),
        Paragraph("WHO NEEDS TO BE LOOPED IN", s["header"]),
        ListFlowable(
            [ListItem(Paragraph(item, s["body"])) for item in who_items],
            bulletType="bullet",
            leftIndent=18,
        ),
        Spacer(1, 0.08 * inch),
        Paragraph("OPEN ITEMS / BLOCKERS", s["header"]),
        ListFlowable(
            [ListItem(Paragraph(item, s["body"])) for item in blocker_items],
            bulletType="1",
            start="1",
            leftIndent=18,
        ),
    ]

    doc.build(story)
    print(OUTPUT)


if __name__ == "__main__":
    build()
