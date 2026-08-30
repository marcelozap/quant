#!/usr/bin/env python3
"""Generate synthetic retail-lakehouse inputs for Store Pulse."""

from __future__ import annotations

import csv
import random
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
SEED = 42


@dataclass(frozen=True)
class Item:
    item_id: str
    name: str
    category: str
    department: str
    perishable: bool
    base_price: float
    base_hourly_demand: float


STORES = [
    {"store_id": "1001", "store_name": "Fort Lauderdale East"},
    {"store_id": "1002", "store_name": "Pembroke Pines"},
    {"store_id": "1003", "store_name": "Davie"},
]

ITEMS = [
    Item("SKU001", "Bananas", "produce", "produce", True, 0.69, 10.5),
    Item("SKU002", "Avocados", "produce", "produce", True, 1.49, 4.0),
    Item("SKU003", "Whole Milk", "dairy", "dairy", True, 4.29, 3.4),
    Item("SKU004", "Greek Yogurt", "dairy", "dairy", True, 1.39, 2.8),
    Item("SKU005", "Chicken Breast", "meat", "meat", True, 8.49, 2.6),
    Item("SKU006", "Ground Beef", "meat", "meat", True, 7.99, 2.2),
    Item("SKU007", "Italian Bread", "bakery", "bakery", True, 3.99, 2.4),
    Item("SKU008", "Croissants", "bakery", "bakery", True, 4.99, 1.7),
    Item("SKU009", "Sparkling Water", "beverages", "grocery", False, 5.49, 1.8),
    Item("SKU010", "Orange Juice", "beverages", "grocery", True, 4.99, 2.0),
    Item("SKU011", "Frozen Pizza", "frozen", "frozen", False, 6.99, 1.4),
    Item("SKU012", "Ice Cream", "frozen", "frozen", False, 5.99, 1.5),
    Item("SKU013", "Peanut Butter", "grocery", "grocery", False, 3.49, 1.3),
    Item("SKU014", "Pasta", "grocery", "grocery", False, 1.89, 1.2),
    Item("SKU015", "Paper Towels", "household", "grocery", False, 12.99, 0.7),
]

PROMO_ITEMS = {"SKU001", "SKU003", "SKU009", "SKU011"}


def ensure_dirs() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)


def daterange(start: date, days: int) -> list[date]:
    return [start + timedelta(days=offset) for offset in range(days)]


def hours_for_day(day: date) -> list[datetime]:
    start = datetime.combine(day, time(6, 0))
    return [start + timedelta(hours=offset) for offset in range(16)]


def promo_flag(item_id: str, dt: datetime) -> bool:
    return item_id in PROMO_ITEMS and dt.weekday() in {4, 5, 6}


def weather_score(day: date) -> tuple[int, str]:
    temp = random.randint(78, 95)
    condition = random.choice(["sunny", "humid", "stormy", "cloudy"])
    return temp, condition


def generate_pos_transactions(days: list[date]) -> None:
    path = RAW_DIR / "pos_transactions.csv"
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "event_ts",
                "store_id",
                "store_name",
                "item_id",
                "item_name",
                "category",
                "department",
                "quantity",
                "unit_price",
                "net_sales",
                "promo_flag",
            ],
        )
        writer.writeheader()
        for day in days:
            for hour_ts in hours_for_day(day):
                time_multiplier = 1.3 if hour_ts.hour in {11, 12, 17, 18} else 0.9
                for store in STORES:
                    store_multiplier = 1.1 if store["store_id"] == "1001" else 1.0
                    for item in ITEMS:
                        demand = item.base_hourly_demand * time_multiplier * store_multiplier
                        if promo_flag(item.item_id, hour_ts):
                            demand *= 1.45
                        units = max(0, int(random.gauss(demand, max(1.0, demand * 0.25))))
                        if units == 0:
                            continue
                        price = item.base_price * (0.9 if promo_flag(item.item_id, hour_ts) else 1.0)
                        writer.writerow(
                            {
                                "event_ts": hour_ts.isoformat(),
                                "store_id": store["store_id"],
                                "store_name": store["store_name"],
                                "item_id": item.item_id,
                                "item_name": item.name,
                                "category": item.category,
                                "department": item.department,
                                "quantity": units,
                                "unit_price": f"{price:.2f}",
                                "net_sales": f"{units * price:.2f}",
                                "promo_flag": str(promo_flag(item.item_id, hour_ts)).lower(),
                            }
                        )


def generate_inventory_snapshots(days: list[date]) -> None:
    path = RAW_DIR / "inventory_snapshots.csv"
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "snapshot_ts",
                "store_id",
                "item_id",
                "category",
                "department",
                "on_hand_units",
                "backroom_units",
            ],
        )
        writer.writeheader()
        for day in days:
            for hour_ts in hours_for_day(day):
                for store in STORES:
                    for item in ITEMS:
                        base = 18 if item.perishable else 28
                        demand_drag = int(item.base_hourly_demand * (hour_ts.hour - 5) * 0.35)
                        promo_drag = 4 if promo_flag(item.item_id, hour_ts) else 0
                        on_hand = max(0, base - demand_drag - promo_drag + random.randint(-3, 5))
                        backroom = max(0, int(base * 0.6) + random.randint(-2, 4))
                        writer.writerow(
                            {
                                "snapshot_ts": hour_ts.isoformat(),
                                "store_id": store["store_id"],
                                "item_id": item.item_id,
                                "category": item.category,
                                "department": item.department,
                                "on_hand_units": on_hand,
                                "backroom_units": backroom,
                            }
                        )


def generate_deliveries(days: list[date]) -> None:
    path = RAW_DIR / "deliveries.csv"
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "delivery_ts",
                "store_id",
                "item_id",
                "delivery_units",
                "vendor_name",
            ],
        )
        writer.writeheader()
        for day in days:
            delivery_ts = datetime.combine(day, time(5, 30))
            for store in STORES:
                for item in ITEMS:
                    if item.perishable or random.random() < 0.55:
                        writer.writerow(
                            {
                                "delivery_ts": delivery_ts.isoformat(),
                                "store_id": store["store_id"],
                                "item_id": item.item_id,
                                "delivery_units": max(6, int(item.base_hourly_demand * 8 + random.randint(0, 10))),
                                "vendor_name": random.choice(["FreshSource", "Regional DC", "Local Vendor"]),
                            }
                        )


def generate_promotions(days: list[date]) -> None:
    path = RAW_DIR / "promotions.csv"
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["item_id", "promo_start", "promo_end", "promo_type", "discount_pct"],
        )
        writer.writeheader()
        start = days[0]
        end = days[-1]
        for item_id in sorted(PROMO_ITEMS):
            writer.writerow(
                {
                    "item_id": item_id,
                    "promo_start": start.isoformat(),
                    "promo_end": end.isoformat(),
                    "promo_type": random.choice(["weekly ad", "digital coupon", "feature"]),
                    "discount_pct": random.choice([10, 15, 20]),
                }
            )


def generate_labor_schedule(days: list[date]) -> None:
    path = RAW_DIR / "labor_schedule.csv"
    departments = ["produce", "dairy", "meat", "bakery", "grocery", "frozen"]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["business_date", "store_id", "department", "scheduled_hours"],
        )
        writer.writeheader()
        for day in days:
            weekend_boost = 1.15 if day.weekday() in {5, 6} else 1.0
            for store in STORES:
                for department in departments:
                    base = 22 if department == "grocery" else 14
                    writer.writerow(
                        {
                            "business_date": day.isoformat(),
                            "store_id": store["store_id"],
                            "department": department,
                            "scheduled_hours": f"{base * weekend_boost + random.uniform(-2.0, 2.5):.1f}",
                        }
                    )


def generate_weather(days: list[date]) -> None:
    path = RAW_DIR / "weather_daily.csv"
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["business_date", "store_id", "temp_f", "condition"],
        )
        writer.writeheader()
        for day in days:
            for store in STORES:
                temp, condition = weather_score(day)
                writer.writerow(
                    {
                        "business_date": day.isoformat(),
                        "store_id": store["store_id"],
                        "temp_f": temp,
                        "condition": condition,
                    }
                )


def generate_waste(days: list[date]) -> None:
    path = RAW_DIR / "waste_events.csv"
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["business_date", "store_id", "item_id", "waste_units", "reason_code"],
        )
        writer.writeheader()
        for day in days:
            for store in STORES:
                for item in ITEMS:
                    if not item.perishable:
                        continue
                    waste = max(0, int(random.gauss(1.4, 1.2)))
                    if waste == 0:
                        continue
                    writer.writerow(
                        {
                            "business_date": day.isoformat(),
                            "store_id": store["store_id"],
                            "item_id": item.item_id,
                            "waste_units": waste,
                            "reason_code": random.choice(["damage", "expired", "quality"]),
                        }
                    )


def main() -> None:
    random.seed(SEED)
    ensure_dirs()
    start = date.today() - timedelta(days=13)
    days = daterange(start, 14)
    generate_pos_transactions(days)
    generate_inventory_snapshots(days)
    generate_deliveries(days)
    generate_promotions(days)
    generate_labor_schedule(days)
    generate_weather(days)
    generate_waste(days)
    print(f"Wrote sample raw files to {RAW_DIR}")


if __name__ == "__main__":
    main()
