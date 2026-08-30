#!/usr/bin/env python3
"""Build gold marts from synthetic retail Store Pulse raw data."""

from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
GOLD_DIR = ROOT / "data" / "gold"


PERISHABLE_CATEGORIES = {"produce", "dairy", "meat", "bakery"}


def read_csv(name: str) -> list[dict[str, str]]:
    path = RAW_DIR / name
    with path.open() as handle:
        return list(csv.DictReader(handle))


def write_csv(name: str, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    path = GOLD_DIR / name
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_hourly_sales(pos_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    hourly = defaultdict(lambda: {"units_sold": 0, "net_sales": 0.0, "promo_flag": False})
    for row in pos_rows:
        hour_key = row["event_ts"][:13] + ":00:00"
        key = (row["store_id"], row["item_id"], row["category"], row["department"], hour_key)
        hourly[key]["units_sold"] += int(row["quantity"])
        hourly[key]["net_sales"] += float(row["net_sales"])
        hourly[key]["promo_flag"] = hourly[key]["promo_flag"] or row["promo_flag"] == "true"

    records = []
    for key, metrics in sorted(hourly.items()):
        store_id, item_id, category, department, hour_ts = key
        records.append(
            {
                "store_id": store_id,
                "item_id": item_id,
                "category": category,
                "department": department,
                "hour_ts": hour_ts,
                "units_sold": metrics["units_sold"],
                "net_sales": f"{metrics['net_sales']:.2f}",
                "promo_flag": str(metrics["promo_flag"]).lower(),
            }
        )
    return records


def latest_inventory_by_item(inventory_rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    latest: dict[tuple[str, str], dict[str, str]] = {}
    for row in inventory_rows:
        key = (row["store_id"], row["item_id"])
        current_ts = datetime.fromisoformat(row["snapshot_ts"])
        if key not in latest or current_ts > datetime.fromisoformat(latest[key]["snapshot_ts"]):
            latest[key] = row
    return latest


def latest_delivery_by_item(delivery_rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    latest: dict[tuple[str, str], dict[str, str]] = {}
    for row in delivery_rows:
        key = (row["store_id"], row["item_id"])
        current_ts = datetime.fromisoformat(row["delivery_ts"])
        if key not in latest or current_ts > datetime.fromisoformat(latest[key]["delivery_ts"]):
            latest[key] = row
    return latest


def build_replenishment_priority(
    hourly_sales: list[dict[str, object]],
    inventory_rows: list[dict[str, str]],
    delivery_rows: list[dict[str, str]],
) -> list[dict[str, object]]:
    latest_inventory = latest_inventory_by_item(inventory_rows)
    latest_delivery = latest_delivery_by_item(delivery_rows)
    grouped = defaultdict(list)

    for row in hourly_sales:
        grouped[(row["store_id"], row["item_id"])].append(row)

    results = []
    for (store_id, item_id), rows in grouped.items():
        rows = sorted(rows, key=lambda r: r["hour_ts"])
        recent = rows[-6:]
        avg_units_per_hour = sum(int(r["units_sold"]) for r in recent) / max(1, len(recent))
        category = rows[-1]["category"]
        department = rows[-1]["department"]
        promo_active = any(r["promo_flag"] == "true" for r in recent)
        inventory = latest_inventory[(store_id, item_id)]
        on_hand_units = int(inventory["on_hand_units"])
        backroom_units = int(inventory["backroom_units"])
        hours_of_supply = round(on_hand_units / avg_units_per_hour, 2) if avg_units_per_hour > 0 else 999.0

        delivery = latest_delivery.get((store_id, item_id))
        last_delivery_ts = delivery["delivery_ts"] if delivery else ""
        perishable_penalty = 18 if category in PERISHABLE_CATEGORIES else 8
        promo_penalty = 14 if promo_active else 0
        low_supply_penalty = 30 if hours_of_supply < 3 else 18 if hours_of_supply < 6 else 0
        velocity_penalty = min(25, int(avg_units_per_hour * 1.8))
        backroom_relief = 12 if backroom_units > on_hand_units else 0
        urgency_score = max(0, min(100, perishable_penalty + promo_penalty + low_supply_penalty + velocity_penalty - backroom_relief))

        if urgency_score >= 75:
            status = "critical"
        elif urgency_score >= 55:
            status = "high"
        elif urgency_score >= 35:
            status = "watch"
        else:
            status = "stable"

        results.append(
            {
                "store_id": store_id,
                "item_id": item_id,
                "category": category,
                "department": department,
                "avg_units_per_hour_6h": f"{avg_units_per_hour:.2f}",
                "on_hand_units": on_hand_units,
                "backroom_units": backroom_units,
                "hours_of_supply": f"{hours_of_supply:.2f}",
                "promo_active": str(promo_active).lower(),
                "last_delivery_ts": last_delivery_ts,
                "urgency_score": urgency_score,
                "priority_status": status,
            }
        )

    results.sort(key=lambda row: (-int(row["urgency_score"]), row["store_id"], row["item_id"]))
    return results


def build_promo_review(hourly_sales: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped = defaultdict(lambda: {"promo_units": [], "base_units": [], "promo_sales": [], "base_sales": [], "category": ""})
    for row in hourly_sales:
        key = (row["store_id"], row["item_id"])
        grouped[key]["category"] = row["category"]
        units = int(row["units_sold"])
        sales = float(row["net_sales"])
        if row["promo_flag"] == "true":
            grouped[key]["promo_units"].append(units)
            grouped[key]["promo_sales"].append(sales)
        else:
            grouped[key]["base_units"].append(units)
            grouped[key]["base_sales"].append(sales)

    results = []
    for (store_id, item_id), metrics in grouped.items():
        if not metrics["promo_units"]:
            continue
        promo_avg_units = sum(metrics["promo_units"]) / len(metrics["promo_units"])
        base_avg_units = sum(metrics["base_units"]) / max(1, len(metrics["base_units"]))
        promo_avg_sales = sum(metrics["promo_sales"]) / len(metrics["promo_sales"])
        base_avg_sales = sum(metrics["base_sales"]) / max(1, len(metrics["base_sales"]))
        unit_lift_ratio = promo_avg_units / base_avg_units if base_avg_units > 0 else 0.0
        if unit_lift_ratio >= 1.35:
            promo_status = "strong"
        elif unit_lift_ratio >= 1.10:
            promo_status = "working"
        else:
            promo_status = "weak"
        results.append(
            {
                "store_id": store_id,
                "item_id": item_id,
                "category": metrics["category"],
                "promo_avg_units_per_hour": f"{promo_avg_units:.2f}",
                "baseline_avg_units_per_hour": f"{base_avg_units:.2f}",
                "unit_lift_ratio": f"{unit_lift_ratio:.2f}",
                "promo_avg_sales_per_hour": f"{promo_avg_sales:.2f}",
                "baseline_avg_sales_per_hour": f"{base_avg_sales:.2f}",
                "promo_status": promo_status,
            }
        )
    results.sort(key=lambda row: (-float(row["unit_lift_ratio"]), row["store_id"], row["item_id"]))
    return results


def build_fresh_risk(
    replenishment_rows: list[dict[str, object]],
    waste_rows: list[dict[str, str]],
) -> list[dict[str, object]]:
    waste_totals = defaultdict(int)
    for row in waste_rows:
        waste_totals[(row["store_id"], row["item_id"])] += int(row["waste_units"])

    results = []
    for row in replenishment_rows:
        if row["category"] not in PERISHABLE_CATEGORIES:
            continue
        waste_units_14d = waste_totals[(row["store_id"], row["item_id"])]
        hours_of_supply = float(row["hours_of_supply"])
        urgency = int(row["urgency_score"])
        fresh_risk_score = min(100, urgency + waste_units_14d * 4 + (15 if hours_of_supply < 4 else 0))
        if fresh_risk_score >= 80:
            risk_status = "critical"
        elif fresh_risk_score >= 60:
            risk_status = "high"
        elif fresh_risk_score >= 40:
            risk_status = "watch"
        else:
            risk_status = "stable"
        results.append(
            {
                "store_id": row["store_id"],
                "item_id": row["item_id"],
                "category": row["category"],
                "hours_of_supply": row["hours_of_supply"],
                "waste_units_14d": waste_units_14d,
                "urgency_score": urgency,
                "fresh_risk_score": fresh_risk_score,
                "risk_status": risk_status,
            }
        )
    results.sort(key=lambda row: (-int(row["fresh_risk_score"]), row["store_id"], row["item_id"]))
    return results


def print_summary(replenishment: list[dict[str, object]], promo_review: list[dict[str, object]], fresh_risk: list[dict[str, object]]) -> None:
    print("Top replenishment priorities:")
    for row in replenishment[:5]:
        print(
            f"  store {row['store_id']} {row['item_id']} "
            f"score={row['urgency_score']} supply={row['hours_of_supply']}h status={row['priority_status']}"
        )

    print("\nTop promo performers:")
    for row in promo_review[:5]:
        print(
            f"  store {row['store_id']} {row['item_id']} "
            f"lift={row['unit_lift_ratio']} status={row['promo_status']}"
        )

    print("\nTop fresh risks:")
    for row in fresh_risk[:5]:
        print(
            f"  store {row['store_id']} {row['item_id']} "
            f"risk={row['fresh_risk_score']} waste={row['waste_units_14d']} status={row['risk_status']}"
        )


def main() -> None:
    pos_rows = read_csv("pos_transactions.csv")
    inventory_rows = read_csv("inventory_snapshots.csv")
    delivery_rows = read_csv("deliveries.csv")
    waste_rows = read_csv("waste_events.csv")

    hourly_sales = build_hourly_sales(pos_rows)
    replenishment = build_replenishment_priority(hourly_sales, inventory_rows, delivery_rows)
    promo_review = build_promo_review(hourly_sales)
    fresh_risk = build_fresh_risk(replenishment, waste_rows)

    write_csv(
        "gold_store_item_hourly.csv",
        hourly_sales,
        ["store_id", "item_id", "category", "department", "hour_ts", "units_sold", "net_sales", "promo_flag"],
    )
    write_csv(
        "gold_replenishment_priority.csv",
        replenishment,
        [
            "store_id",
            "item_id",
            "category",
            "department",
            "avg_units_per_hour_6h",
            "on_hand_units",
            "backroom_units",
            "hours_of_supply",
            "promo_active",
            "last_delivery_ts",
            "urgency_score",
            "priority_status",
        ],
    )
    write_csv(
        "gold_promo_review.csv",
        promo_review,
        [
            "store_id",
            "item_id",
            "category",
            "promo_avg_units_per_hour",
            "baseline_avg_units_per_hour",
            "unit_lift_ratio",
            "promo_avg_sales_per_hour",
            "baseline_avg_sales_per_hour",
            "promo_status",
        ],
    )
    write_csv(
        "gold_fresh_risk.csv",
        fresh_risk,
        [
            "store_id",
            "item_id",
            "category",
            "hours_of_supply",
            "waste_units_14d",
            "urgency_score",
            "fresh_risk_score",
            "risk_status",
        ],
    )

    print_summary(replenishment, promo_review, fresh_risk)
    print(f"\nWrote gold outputs to {GOLD_DIR}")


if __name__ == "__main__":
    main()
