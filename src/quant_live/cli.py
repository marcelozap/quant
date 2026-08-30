"""Command-line interface for live data and account snapshots."""

from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime
import json
import time
from pathlib import Path

from quant_live.activity import (
    append_activity,
    build_daily_readme,
    load_activities_for_date,
    summarize_activities,
    write_daily_readme,
)
from quant_live.auth import refresh_access_token
from quant_live.client import SchwabClient
from quant_live.config import Settings
from quant_live.execution import (
    load_execution_rows,
    render_execution_report_markdown,
    summarize_execution_rows,
    write_execution_summary,
)
from quant_live.green_machine_api import run_local_server
from quant_live.green_machine_intake import inventory_candidates
from quant_live.green_machine_imports import import_options_trade_csv, preview_trade_csv
from quant_live.green_machine_analytics import summarize_closed_trades
from quant_live.green_machine_store import GreenMachineStore
from quant_live.research import (
    available_watchlists,
    build_signal_sheet_entries,
    bundle_end_of_day,
    flatten_quote_payload,
    latest_snapshot_path,
    latest_snapshot_paths,
    load_snapshot,
    render_signal_sheet_markdown,
    render_dashboard_markdown,
    render_history_sheet_markdown,
    render_snapshot_comparison_markdown,
    render_snapshot_markdown,
    summarize_watchlist_history,
    load_signal_sheet_entries,
    write_html_export,
    write_snapshot_csv,
    write_signal_sheet,
    write_snapshot,
)
from quant_live.templates import WATCHLIST_TEMPLATES


def _print_json(payload: object) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _log_activity(settings: Settings, command: str, symbols: list[str] | None = None, note: str = "") -> None:
    append_activity(
        settings.activity_log_path,
        {
            "command": command,
            "symbols": symbols or [],
            "note": note,
        },
    )


def _today_str() -> str:
    return datetime.now().astimezone().date().isoformat()


def _capture_watchlist_snapshot(
    settings: Settings,
    name: str,
    symbols: list[str],
    fields: str,
    batch_size: int,
    command_name: str,
) -> tuple[str, str, str, str]:
    client = SchwabClient(settings)
    payloads = client.quote_batches(symbols, fields=fields, batch_size=batch_size)
    rows = flatten_quote_payload(payloads)
    json_path = write_snapshot(
        settings.research_snapshot_dir,
        name,
        rows,
        average_weight=settings.score_average_weight,
        dispersion_weight=settings.score_dispersion_weight,
    )
    csv_path = write_snapshot_csv(settings.research_snapshot_dir, name, rows)
    markdown = render_snapshot_markdown(
        name,
        rows,
        average_weight=settings.score_average_weight,
        dispersion_weight=settings.score_dispersion_weight,
    )
    html_path = write_html_export(settings.html_export_dir, f"snapshot_{name}", _today_str(), markdown)
    _log_activity(
        settings,
        command_name,
        symbols=symbols,
        note=f"name={name}, rows={len(rows)}, json={json_path}, csv={csv_path}, html={html_path}",
    )
    return json_path, csv_path, html_path, markdown


def cmd_quote(args: argparse.Namespace) -> None:
    settings = Settings.from_env()
    client = SchwabClient(settings)
    payload = client.quotes(args.symbols, fields=args.fields)
    _log_activity(settings, "quote", symbols=args.symbols, note=f"fields={args.fields}")
    _print_json(payload)


def cmd_poll_quotes(args: argparse.Namespace) -> None:
    settings = Settings.from_env()
    client = SchwabClient(settings)
    rounds = 0
    while args.rounds <= 0 or rounds < args.rounds:
        payload = {
            "timestamp": time.time(),
            "round": rounds + 1,
            "batches": client.quote_batches(
                args.symbols,
                fields=args.fields,
                batch_size=args.batch_size,
            ),
        }
        _log_activity(
            settings,
            "poll-quotes",
            symbols=args.symbols,
            note=f"round={rounds + 1}, batch_size={args.batch_size or settings.quote_batch_size}",
        )
        _print_json(payload)
        rounds += 1
        if args.rounds > 0 and rounds >= args.rounds:
            return
        time.sleep(args.interval_seconds)


def cmd_account_numbers(_: argparse.Namespace) -> None:
    settings = Settings.from_env()
    client = SchwabClient(settings)
    payload = client.account_numbers()
    _log_activity(settings, "account-numbers")
    _print_json(payload)


def cmd_accounts(args: argparse.Namespace) -> None:
    settings = Settings.from_env()
    client = SchwabClient(settings)
    if args.account_hash:
        payload = client.account(account_hash=args.account_hash, fields=args.fields)
        _log_activity(settings, "accounts", note=f"single_account fields={args.fields}")
        _print_json(payload)
        return
    payload = client.accounts(fields=args.fields)
    _log_activity(settings, "accounts", note=f"all_accounts fields={args.fields}")
    _print_json(payload)


def cmd_price_history(args: argparse.Namespace) -> None:
    settings = Settings.from_env()
    client = SchwabClient(settings)
    payload = client.price_history(
        args.symbol,
        period_type=args.period_type,
        period=args.period,
        frequency_type=args.frequency_type,
        frequency=args.frequency,
        need_extended_hours_data=args.extended_hours,
        need_previous_close=args.previous_close,
    )
    _log_activity(
        settings,
        "price-history",
        symbols=[args.symbol],
        note=f"period_type={args.period_type}, period={args.period}, frequency_type={args.frequency_type}, frequency={args.frequency}",
    )
    _print_json(payload)


def cmd_refresh_token(_: argparse.Namespace) -> None:
    settings = Settings.from_env()
    payload = refresh_access_token(settings)
    _log_activity(settings, "refresh-token", note="refreshed access token")
    _print_json(payload)


def cmd_rate_limit(_: argparse.Namespace) -> None:
    settings = Settings.from_env()
    settings.require_access_token()
    client = SchwabClient(settings)
    payload = asdict(client.rate_limit_status())
    payload["configured_rate_limit_per_minute"] = settings.rate_limit_per_minute
    payload["reserve_calls_per_minute"] = settings.reserve_calls_per_minute
    payload["effective_calls_per_minute"] = settings.effective_calls_per_minute
    _log_activity(settings, "rate-limit", note="checked current shared budget")
    _print_json(payload)


def cmd_daily_readme(args: argparse.Namespace) -> None:
    settings = Settings.from_env()
    date_str = args.date or _today_str()
    entries = load_activities_for_date(settings.activity_log_path, date_str)
    summary = summarize_activities(entries, date_str)
    markdown = build_daily_readme(summary)
    path = write_daily_readme(settings.daily_readme_dir, date_str, markdown)
    _log_activity(settings, "daily-readme", note=f"wrote {path}")
    print(path)


def cmd_green_machine_inventory(args: argparse.Namespace) -> None:
    roots = args.roots or ["~/Documents", "~/Downloads", "~/Desktop"]
    payload = inventory_candidates(roots, max_results=args.max_results)
    _print_json({"roots": roots, "results": payload, "metadata_only": True})


def cmd_green_machine_init(_: argparse.Namespace) -> None:
    settings = Settings.from_env()
    store = GreenMachineStore(settings.green_machine_data_dir)
    store.initialize()
    print(store.database_path)


def cmd_green_machine_serve(_: argparse.Namespace) -> None:
    settings = Settings.from_env()
    run_local_server(settings, GreenMachineStore(settings.green_machine_data_dir))


def cmd_green_machine_capture_account(args: argparse.Namespace) -> None:
    settings = Settings.from_env()
    client = SchwabClient(settings)
    store = GreenMachineStore(settings.green_machine_data_dir)
    store.initialize()
    payload = client.account(account_hash=args.account_hash, fields="positions") if args.account_hash else client.accounts(fields="positions")
    snapshot = store.put(
        "account_snapshot",
        {"source": "schwab", "captured_at": datetime.now().astimezone().isoformat(), "payload": payload},
    )
    _log_activity(settings, "green-machine-capture-account", note=f"stored encrypted snapshot id={snapshot['id']}")
    print(snapshot["id"])


def cmd_green_machine_preview_import(args: argparse.Namespace) -> None:
    _print_json(preview_trade_csv(args.source_path))


def cmd_green_machine_import_trades(args: argparse.Namespace) -> None:
    settings = Settings.from_env()
    store = GreenMachineStore(settings.green_machine_data_dir)
    store.initialize()
    result = import_options_trade_csv(args.source_path, store)
    _log_activity(settings, "green-machine-import-trades", note=f"source={args.source_path}, trades_written={result['trades_written']}")
    _print_json(result)


def cmd_green_machine_analytics(_: argparse.Namespace) -> None:
    settings = Settings.from_env()
    store = GreenMachineStore(settings.green_machine_data_dir)
    _print_json(summarize_closed_trades(store.list("trade", limit=10_000)))


def cmd_green_machine_daily_review(args: argparse.Namespace) -> None:
    settings = Settings.from_env()
    store = GreenMachineStore(settings.green_machine_data_dir)
    store.initialize()
    date = args.date or _today_str()
    review = store.put(
        "daily_review",
        {
            "date": date,
            "focus": args.focus,
            "observation": args.observation,
            "strength": args.strength,
            "lesson": args.lesson,
            "open_question": args.open_question,
        },
        record_id=f"daily-review:{date}",
    )
    song = None
    if args.song_title:
        song = store.put(
            "song_memory",
            {"date": date, "title": args.song_title, "link": args.song_link, "mood": args.song_mood},
            record_id=f"song-memory:{date}",
        )
    _log_activity(settings, "green-machine-daily-review", note=f"date={date}")
    _print_json({"daily_review": review, "song_memory": song})


def cmd_watchlist_snapshot(args: argparse.Namespace) -> None:
    settings = Settings.from_env()
    json_path, csv_path, html_path, markdown = _capture_watchlist_snapshot(
        settings,
        args.name,
        args.symbols,
        args.fields,
        args.batch_size,
        "watchlist-snapshot",
    )
    print(json_path)
    print(csv_path)
    print(html_path)
    if args.print_summary:
        print("")
        print(markdown)


def cmd_compare_watchlist(args: argparse.Namespace) -> None:
    settings = Settings.from_env()
    paths = latest_snapshot_paths(settings.research_snapshot_dir, args.name, limit=2)
    if len(paths) < 2:
        raise ValueError(f"need at least two snapshots for watchlist '{args.name}'")
    previous_payload = load_snapshot(paths[0])
    current_payload = load_snapshot(paths[1])
    markdown = render_snapshot_comparison_markdown(args.name, previous_payload, current_payload)
    _log_activity(settings, "compare-watchlist", note=f"name={args.name}, previous={paths[0]}, current={paths[1]}")
    print(markdown)


def cmd_signal_sheet(args: argparse.Namespace) -> None:
    settings = Settings.from_env()
    names = args.watchlists or available_watchlists(settings.research_snapshot_dir)
    payloads = {}
    for name in names:
        path = latest_snapshot_path(settings.research_snapshot_dir, name)
        if not path:
            continue
        payloads[name] = load_snapshot(path)

    date_str = args.date or _today_str()
    entries = build_signal_sheet_entries(payloads)
    markdown = render_signal_sheet_markdown(entries, date_str)
    path = write_signal_sheet(settings.signal_sheet_dir, date_str, markdown)
    html_path = write_html_export(settings.html_export_dir, "signal_sheet", date_str, markdown)
    _log_activity(settings, "signal-sheet", note=f"watchlists={','.join(names)}, path={path}, html={html_path}")
    print(path)
    print(html_path)
    if args.print_summary:
        print("")
        print(markdown)


def cmd_list_templates(_: argparse.Namespace) -> None:
    print(json.dumps(WATCHLIST_TEMPLATES, indent=2, sort_keys=True))


def cmd_template_snapshot(args: argparse.Namespace) -> None:
    settings = Settings.from_env()
    symbols = WATCHLIST_TEMPLATES[args.template]
    json_path, csv_path, html_path, markdown = _capture_watchlist_snapshot(
        settings,
        args.template,
        symbols,
        args.fields,
        args.batch_size,
        "template-snapshot",
    )
    print(json_path)
    print(csv_path)
    print(html_path)
    if args.print_summary:
        print("")
        print(markdown)


def cmd_dashboard(args: argparse.Namespace) -> None:
    settings = Settings.from_env()
    date_str = args.date or _today_str()
    signal_sheet_path = str(Path(settings.signal_sheet_dir) / f"{date_str}.md")
    if not Path(signal_sheet_path).exists():
        signal_sheet_path = None

    daily_readme_path = str(Path(settings.daily_readme_dir) / f"{date_str}.md")
    if not Path(daily_readme_path).exists():
        daily_readme_path = None

    names = available_watchlists(settings.research_snapshot_dir)
    payloads = {}
    for name in names:
        path = latest_snapshot_path(settings.research_snapshot_dir, name)
        if path:
            payloads[name] = load_snapshot(path)
    entries = build_signal_sheet_entries(payloads)
    markdown = render_dashboard_markdown(date_str, signal_sheet_path, daily_readme_path, entries)
    output_path = Path(settings.dashboard_dir) / f"{date_str}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    html_path = write_html_export(settings.html_export_dir, "dashboard", date_str, markdown)
    _log_activity(settings, "dashboard", note=f"path={output_path}, html={html_path}")
    print(str(output_path))
    print(html_path)
    if args.print_summary:
        print("")
        print(markdown)


def cmd_end_of_day_bundle(args: argparse.Namespace) -> None:
    settings = Settings.from_env()
    date_str = args.date or _today_str()
    signal_sheet_path = str(Path(settings.signal_sheet_dir) / f"{date_str}.md")
    if not Path(signal_sheet_path).exists():
        signal_sheet_path = None
    daily_readme_path = str(Path(settings.daily_readme_dir) / f"{date_str}.md")
    if not Path(daily_readme_path).exists():
        daily_readme_path = None
    dashboard_path = str(Path(settings.dashboard_dir) / f"{date_str}.md")
    if not Path(dashboard_path).exists():
        dashboard_path = None

    bundle_path = bundle_end_of_day(
        settings.end_of_day_bundle_dir,
        date_str,
        signal_sheet_path,
        daily_readme_path,
        dashboard_path,
    )
    _log_activity(settings, "end-of-day-bundle", note=f"path={bundle_path}")
    print(bundle_path)


def cmd_history_sheet(args: argparse.Namespace) -> None:
    settings = Settings.from_env()
    rows = load_signal_sheet_entries(settings.signal_sheet_dir)
    summary = summarize_watchlist_history(rows, lookback=args.lookback)
    markdown = render_history_sheet_markdown(summary, args.lookback)
    date_str = _today_str()
    output_path = Path(settings.history_dir) / f"{date_str}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    html_path = write_html_export(settings.html_export_dir, "history_sheet", date_str, markdown)
    _log_activity(settings, "history-sheet", note=f"path={output_path}, html={html_path}, lookback={args.lookback}")
    print(str(output_path))
    print(html_path)
    if args.print_summary:
        print("")
        print(markdown)


def cmd_tca_report(args: argparse.Namespace) -> None:
    settings = Settings.from_env()
    report_name = args.name or Path(args.input_path).stem
    rows = load_execution_rows(args.input_path)
    summary = summarize_execution_rows(rows)
    markdown = render_execution_report_markdown(report_name, summary)
    output_path = Path(settings.execution_report_dir) / f"{report_name}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    json_path = write_execution_summary(settings.execution_report_dir, report_name, summary)
    html_path = write_html_export(settings.html_export_dir, f"execution_{report_name}", _today_str(), markdown)
    _log_activity(
        settings,
        "tca-report",
        note=f"input={args.input_path}, markdown={output_path}, json={json_path}, html={html_path}",
    )
    print(str(output_path))
    print(json_path)
    print(html_path)
    if args.print_summary:
        print("")
        print(markdown)


def cmd_research_pack(args: argparse.Namespace) -> None:
    settings = Settings.from_env()
    templates = args.templates or sorted(WATCHLIST_TEMPLATES)
    snapshot_paths: list[str] = []
    for template in templates:
        symbols = WATCHLIST_TEMPLATES[template]
        json_path, csv_path, html_path, _ = _capture_watchlist_snapshot(
            settings,
            template,
            symbols,
            args.fields,
            args.batch_size,
            "research-pack",
        )
        snapshot_paths.extend([json_path, csv_path, html_path])

    date_str = args.date or _today_str()
    payloads = {}
    for template in templates:
        path = latest_snapshot_path(settings.research_snapshot_dir, template)
        if path:
            payloads[template] = load_snapshot(path)

    entries = build_signal_sheet_entries(payloads)
    signal_markdown = render_signal_sheet_markdown(entries, date_str)
    signal_path = write_signal_sheet(settings.signal_sheet_dir, date_str, signal_markdown)
    signal_html = write_html_export(settings.html_export_dir, "signal_sheet", date_str, signal_markdown)

    daily_entries = load_activities_for_date(settings.activity_log_path, date_str)
    daily_summary = summarize_activities(daily_entries, date_str)
    daily_markdown = build_daily_readme(daily_summary)
    daily_path = write_daily_readme(settings.daily_readme_dir, date_str, daily_markdown)

    dashboard_markdown = render_dashboard_markdown(date_str, signal_path, daily_path, entries)
    dashboard_path = Path(settings.dashboard_dir) / f"{date_str}.md"
    dashboard_path.parent.mkdir(parents=True, exist_ok=True)
    dashboard_path.write_text(dashboard_markdown, encoding="utf-8")
    dashboard_html = write_html_export(settings.html_export_dir, "dashboard", date_str, dashboard_markdown)

    bundle_path = bundle_end_of_day(
        settings.end_of_day_bundle_dir,
        date_str,
        signal_path,
        daily_path,
        str(dashboard_path),
    )

    history_rows = load_signal_sheet_entries(settings.signal_sheet_dir)
    history_summary = summarize_watchlist_history(history_rows, lookback=args.lookback)
    history_markdown = render_history_sheet_markdown(history_summary, args.lookback)
    history_path = Path(settings.history_dir) / f"{date_str}.md"
    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.write_text(history_markdown, encoding="utf-8")
    history_html = write_html_export(settings.html_export_dir, "history_sheet", date_str, history_markdown)

    _log_activity(
        settings,
        "research-pack",
        note=f"templates={','.join(templates)}, signal={signal_path}, daily={daily_path}, dashboard={dashboard_path}, history={history_path}, bundle={bundle_path}",
    )

    outputs = {
        "bundle": bundle_path,
        "daily_readme": daily_path,
        "dashboard_html": dashboard_html,
        "dashboard_markdown": str(dashboard_path),
        "history_html": history_html,
        "history_markdown": str(history_path),
        "signal_sheet_html": signal_html,
        "signal_sheet_markdown": signal_path,
        "snapshots": snapshot_paths,
        "templates": templates,
    }
    _print_json(outputs)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Schwab live-data CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    quote_p = sub.add_parser("quote", help="Fetch one or more quotes")
    quote_p.add_argument("symbols", nargs="+")
    quote_p.add_argument("--fields", default="quote")
    quote_p.set_defaults(func=cmd_quote)

    poll_p = sub.add_parser("poll-quotes", help="Poll quotes in batches for one or more rounds")
    poll_p.add_argument("symbols", nargs="+")
    poll_p.add_argument("--fields", default="quote")
    poll_p.add_argument("--batch-size", type=int, default=0)
    poll_p.add_argument("--interval-seconds", type=float, default=5.0)
    poll_p.add_argument("--rounds", type=int, default=1, help="Use 0 for unbounded polling")
    poll_p.set_defaults(func=cmd_poll_quotes)

    acct_num_p = sub.add_parser("account-numbers", help="Fetch account-number mapping")
    acct_num_p.set_defaults(func=cmd_account_numbers)

    accounts_p = sub.add_parser("accounts", help="Fetch accounts or one account snapshot")
    accounts_p.add_argument("--account-hash", default="")
    accounts_p.add_argument("--fields", default="positions")
    accounts_p.set_defaults(func=cmd_accounts)

    history_p = sub.add_parser("price-history", help="Fetch basic price history")
    history_p.add_argument("symbol")
    history_p.add_argument("--period-type", default="day")
    history_p.add_argument("--period", type=int, default=5)
    history_p.add_argument("--frequency-type", default="minute")
    history_p.add_argument("--frequency", type=int, default=1)
    history_p.add_argument("--extended-hours", action="store_true")
    history_p.add_argument("--previous-close", action="store_true")
    history_p.set_defaults(func=cmd_price_history)

    refresh_p = sub.add_parser("refresh-token", help="Exchange a refresh token for an access token")
    refresh_p.set_defaults(func=cmd_refresh_token)

    limit_p = sub.add_parser("rate-limit", help="Show this process's rate-limit budget")
    limit_p.set_defaults(func=cmd_rate_limit)

    readme_p = sub.add_parser("daily-readme", help="Write a daily markdown recap from local activity logs")
    readme_p.add_argument("--date", default="", help="Date in YYYY-MM-DD; defaults to today")
    readme_p.set_defaults(func=cmd_daily_readme)

    snapshot_p = sub.add_parser("watchlist-snapshot", help="Capture and summarize a research watchlist snapshot")
    snapshot_p.add_argument("name", help="Short watchlist name, e.g. semis or indexes")
    snapshot_p.add_argument("symbols", nargs="+")
    snapshot_p.add_argument("--fields", default="quote")
    snapshot_p.add_argument("--batch-size", type=int, default=0)
    snapshot_p.add_argument("--print-summary", action="store_true")
    snapshot_p.set_defaults(func=cmd_watchlist_snapshot)

    compare_p = sub.add_parser("compare-watchlist", help="Compare the last two snapshots for a watchlist")
    compare_p.add_argument("name", help="Watchlist name to compare")
    compare_p.set_defaults(func=cmd_compare_watchlist)

    signal_p = sub.add_parser("signal-sheet", help="Build a nightly signal sheet from latest watchlist snapshots")
    signal_p.add_argument("watchlists", nargs="*", help="Optional explicit watchlist names")
    signal_p.add_argument("--date", default="", help="Date in YYYY-MM-DD; defaults to today")
    signal_p.add_argument("--print-summary", action="store_true")
    signal_p.set_defaults(func=cmd_signal_sheet)

    templates_p = sub.add_parser("list-templates", help="List built-in watchlist templates")
    templates_p.set_defaults(func=cmd_list_templates)

    template_snap_p = sub.add_parser("template-snapshot", help="Capture a snapshot for a built-in watchlist template")
    template_snap_p.add_argument("template", choices=sorted(WATCHLIST_TEMPLATES))
    template_snap_p.add_argument("--fields", default="quote")
    template_snap_p.add_argument("--batch-size", type=int, default=0)
    template_snap_p.add_argument("--print-summary", action="store_true")
    template_snap_p.set_defaults(func=cmd_template_snapshot)

    dashboard_p = sub.add_parser("dashboard", help="Write a simple markdown dashboard from latest research outputs")
    dashboard_p.add_argument("--date", default="", help="Date in YYYY-MM-DD; defaults to today")
    dashboard_p.add_argument("--print-summary", action="store_true")
    dashboard_p.set_defaults(func=cmd_dashboard)

    eod_p = sub.add_parser("end-of-day-bundle", help="Assemble nightly research artifacts into one folder")
    eod_p.add_argument("--date", default="", help="Date in YYYY-MM-DD; defaults to today")
    eod_p.set_defaults(func=cmd_end_of_day_bundle)

    history_p = sub.add_parser("history-sheet", help="Summarize multi-day watchlist leadership from signal sheets")
    history_p.add_argument("--lookback", type=int, default=5)
    history_p.add_argument("--print-summary", action="store_true")
    history_p.set_defaults(func=cmd_history_sheet)

    tca_p = sub.add_parser("tca-report", help="Analyze an execution blotter and write a desk-style TCA report")
    tca_p.add_argument("input_path", help="CSV or JSON file with execution rows")
    tca_p.add_argument("--name", default="", help="Optional report name; defaults to the input filename stem")
    tca_p.add_argument("--print-summary", action="store_true")
    tca_p.set_defaults(func=cmd_tca_report)

    pack_p = sub.add_parser("research-pack", help="Run the core nightly research pipeline for one or more templates")
    pack_p.add_argument("templates", nargs="*", choices=sorted(WATCHLIST_TEMPLATES))
    pack_p.add_argument("--date", default="", help="Date in YYYY-MM-DD; defaults to today")
    pack_p.add_argument("--fields", default="quote")
    pack_p.add_argument("--batch-size", type=int, default=0)
    pack_p.add_argument("--lookback", type=int, default=5)
    pack_p.set_defaults(func=cmd_research_pack)

    gm_inventory_p = sub.add_parser(
        "green-machine-inventory",
        help="List likely market files by metadata only; never opens file contents",
    )
    gm_inventory_p.add_argument("roots", nargs="*", help="Folders to inspect; defaults to Documents, Downloads, Desktop")
    gm_inventory_p.add_argument("--max-results", type=int, default=500)
    gm_inventory_p.set_defaults(func=cmd_green_machine_inventory)

    gm_init_p = sub.add_parser("green-machine-init", help="Initialize encrypted Green Machine local storage")
    gm_init_p.set_defaults(func=cmd_green_machine_init)

    gm_serve_p = sub.add_parser("green-machine-serve", help="Start the loopback-only Green Machine API")
    gm_serve_p.set_defaults(func=cmd_green_machine_serve)

    gm_account_p = sub.add_parser(
        "green-machine-capture-account",
        help="Capture a read-only Schwab account snapshot into encrypted Green Machine storage",
    )
    gm_account_p.add_argument("--account-hash", default="")
    gm_account_p.set_defaults(func=cmd_green_machine_capture_account)

    gm_preview_import_p = sub.add_parser("green-machine-preview-import", help="Validate a selected options trade CSV without storing it")
    gm_preview_import_p.add_argument("source_path")
    gm_preview_import_p.set_defaults(func=cmd_green_machine_preview_import)

    gm_import_p = sub.add_parser("green-machine-import-trades", help="Encrypt and import a selected options trade CSV")
    gm_import_p.add_argument("source_path")
    gm_import_p.set_defaults(func=cmd_green_machine_import_trades)

    gm_analytics_p = sub.add_parser("green-machine-analytics", help="Summarize imported closed-trade history for review")
    gm_analytics_p.set_defaults(func=cmd_green_machine_analytics)

    gm_daily_p = sub.add_parser("green-machine-daily-review", help="Save a private daily Green Machine review and optional song")
    gm_daily_p.add_argument("--date", default="")
    gm_daily_p.add_argument("--focus", required=True)
    gm_daily_p.add_argument("--observation", default="")
    gm_daily_p.add_argument("--strength", default="")
    gm_daily_p.add_argument("--lesson", default="")
    gm_daily_p.add_argument("--open-question", default="")
    gm_daily_p.add_argument("--song-title", default="")
    gm_daily_p.add_argument("--song-link", default="")
    gm_daily_p.add_argument("--song-mood", default="")
    gm_daily_p.set_defaults(func=cmd_green_machine_daily_review)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
