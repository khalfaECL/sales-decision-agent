"""
sales_api.py — API simulée de données de ventes.

En production, ce fichier serait remplacé par des appels à de vrais endpoints :
Salesforce API, requêtes SQL sur un data warehouse, API REST interne, etc.

Les données contiennent 4 tendances cachées que l'agent doit détecter :
1. Pic de chaises ergonomiques en janvier (bonnes résolutions)
2. Occitanie en déclin constant (-5%/mois)
3. Taux de retour anormal sur le Headset (15% vs 3%)
4. Marge exceptionnelle sur le USB-C Hub (79.5%)
"""

import random
from datetime import datetime, timedelta


# ============================================================
# DONNÉES DE RÉFÉRENCE
# ============================================================

PRODUCTS = {
    "P001": {"name": "Laptop Pro X1", "category": "Electronics", "unit_cost": 450, "unit_price": 899},
    "P002": {"name": "Wireless Headset Z", "category": "Electronics", "unit_cost": 25, "unit_price": 79},
    "P003": {"name": "Office Chair Ergo", "category": "Furniture", "unit_cost": 120, "unit_price": 349},
    "P004": {"name": "Standing Desk Oak", "category": "Furniture", "unit_cost": 200, "unit_price": 599},
    "P005": {"name": "USB-C Hub Ultra", "category": "Accessories", "unit_cost": 8, "unit_price": 39},
    "P006": {"name": "Mechanical Keyboard", "category": "Accessories", "unit_cost": 30, "unit_price": 129},
}

REGIONS = {
    "R01": {"name": "Île-de-France", "sales_multiplier": 1.5},
    "R02": {"name": "Auvergne-Rhône-Alpes", "sales_multiplier": 1.2},
    "R03": {"name": "Nouvelle-Aquitaine", "sales_multiplier": 0.8},
    "R04": {"name": "Occitanie", "sales_multiplier": 0.6},
    "R05": {"name": "Hauts-de-France", "sales_multiplier": 0.9},
}


def _generate_sales_data():
    """Génère 6 mois de données de ventes avec tendances cachées."""
    random.seed(42)
    sales = []
    start_date = datetime(2025, 10, 1)

    for month_offset in range(6):
        current_date = start_date + timedelta(days=30 * month_offset)
        month = current_date.month

        for pid, product in PRODUCTS.items():
            for rid, region in REGIONS.items():
                base_qty = random.randint(10, 50)
                qty = int(base_qty * region["sales_multiplier"])

                # TENDANCE 1 : Pic chaises ergonomiques en janvier
                if pid == "P003" and month == 1:
                    qty = int(qty * 2.5)

                # TENDANCE 2 : Occitanie en déclin constant
                if rid == "R04":
                    decline_factor = 1 - (0.05 * month_offset)
                    qty = max(1, int(qty * decline_factor))

                # TENDANCE 3 : Retours anormaux sur Headset (15% vs 3%)
                if pid == "P002":
                    returns = int(qty * 0.15)
                else:
                    returns = int(qty * 0.03)

                revenue = qty * product["unit_price"]
                cost = qty * product["unit_cost"]

                sales.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "month": current_date.strftime("%Y-%m"),
                    "product_id": pid,
                    "product_name": product["name"],
                    "category": product["category"],
                    "region_id": rid,
                    "region_name": region["name"],
                    "quantity_sold": qty,
                    "returns": returns,
                    "revenue": revenue,
                    "cost": cost,
                    "profit": revenue - cost,
                    "unit_price": product["unit_price"],
                    "unit_cost": product["unit_cost"],
                })

    return sales


# Données pré-générées
_SALES_DATA = _generate_sales_data()


# ============================================================
# ENDPOINTS API
# ============================================================

def get_sales_summary(month: str = None) -> dict:
    """Résumé des ventes, optionnellement filtré par mois (YYYY-MM)."""
    data = _SALES_DATA
    if month:
        data = [s for s in data if s["month"] == month]

    if not data:
        return {"error": f"No data for month {month}"}

    total_revenue = sum(s["revenue"] for s in data)
    total_profit = sum(s["profit"] for s in data)
    total_qty = sum(s["quantity_sold"] for s in data)
    total_returns = sum(s["returns"] for s in data)

    return {
        "period": month or "all (Oct 2025 - Mar 2026)",
        "total_revenue": total_revenue,
        "total_profit": total_profit,
        "margin_pct": round(total_profit / total_revenue * 100, 1),
        "total_units_sold": total_qty,
        "total_returns": total_returns,
        "return_rate_pct": round(total_returns / total_qty * 100, 1),
    }


def get_sales_by_product() -> list:
    """Ventes agrégées par produit."""
    products = {}
    for s in _SALES_DATA:
        pid = s["product_id"]
        if pid not in products:
            products[pid] = {
                "product_id": pid,
                "product_name": s["product_name"],
                "category": s["category"],
                "total_revenue": 0,
                "total_profit": 0,
                "total_qty": 0,
                "total_returns": 0,
            }
        products[pid]["total_revenue"] += s["revenue"]
        products[pid]["total_profit"] += s["profit"]
        products[pid]["total_qty"] += s["quantity_sold"]
        products[pid]["total_returns"] += s["returns"]

    result = []
    for p in products.values():
        p["margin_pct"] = round(p["total_profit"] / p["total_revenue"] * 100, 1)
        p["return_rate_pct"] = round(p["total_returns"] / p["total_qty"] * 100, 1)
        result.append(p)

    return sorted(result, key=lambda x: x["total_revenue"], reverse=True)


def get_sales_by_region() -> list:
    """Ventes agrégées par région avec tendance mensuelle."""
    regions = {}
    for s in _SALES_DATA:
        rid = s["region_id"]
        if rid not in regions:
            regions[rid] = {
                "region_id": rid,
                "region_name": s["region_name"],
                "total_revenue": 0,
                "total_profit": 0,
                "total_qty": 0,
                "months": {},
            }
        regions[rid]["total_revenue"] += s["revenue"]
        regions[rid]["total_profit"] += s["profit"]
        regions[rid]["total_qty"] += s["quantity_sold"]

        m = s["month"]
        if m not in regions[rid]["months"]:
            regions[rid]["months"][m] = 0
        regions[rid]["months"][m] += s["revenue"]

    result = []
    for r in regions.values():
        r["margin_pct"] = round(r["total_profit"] / r["total_revenue"] * 100, 1)
        months_sorted = sorted(r["months"].items())
        if len(months_sorted) >= 2:
            first_rev = months_sorted[0][1]
            last_rev = months_sorted[-1][1]
            r["trend_pct"] = round((last_rev - first_rev) / first_rev * 100, 1)
        r["monthly_revenue"] = dict(months_sorted)
        del r["months"]
        result.append(r)

    return sorted(result, key=lambda x: x["total_revenue"], reverse=True)


def get_product_trend(product_id: str) -> dict:
    """Évolution mensuelle d'un produit spécifique."""
    data = [s for s in _SALES_DATA if s["product_id"] == product_id]
    if not data:
        return {"error": f"Product {product_id} not found"}

    monthly = {}
    for s in data:
        m = s["month"]
        if m not in monthly:
            monthly[m] = {"revenue": 0, "qty": 0, "returns": 0}
        monthly[m]["revenue"] += s["revenue"]
        monthly[m]["qty"] += s["quantity_sold"]
        monthly[m]["returns"] += s["returns"]

    return {
        "product_id": product_id,
        "product_name": data[0]["product_name"],
        "monthly_data": dict(sorted(monthly.items())),
    }
