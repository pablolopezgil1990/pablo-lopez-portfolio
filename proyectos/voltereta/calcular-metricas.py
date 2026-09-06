"""Calcula las métricas estáticas que se copian en app.js.

No convierte los marcadores relativos de Google en fechas.  El cubo «hace un
mes» se conserva únicamente como base y queda fuera de la serie semanal.
"""
from __future__ import annotations

import json
import math
import sys
import unicodedata
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).parent
SOURCE = ROOT / "google-reviews-v3.json"
APP_IDS = {
    "casa-valencia": "casa",
    "bali-valencia": "bali",
    "manhattan-valencia": "manhattan",
    "kioto-valencia": "kioto",
    "nueva-zelanda-zaragoza": "zaragoza",
    "paris-sevilla": "paris",
    "tanzania-alicante": "tanzania",
    "toscana-cordoba": "toscana",
}
WEEKLY_ORDER = ("4 semanas", "3 semanas", "2 semanas", "1 semana", "0-6 días")
DAILY_ORDER = ("-6d", "-5d", "-4d", "-3d", "-2d", "-1d", "hoy")
TIMELINE_ORDER = WEEKLY_ORDER[:-1] + DAILY_ORDER
WEEKDAY_NAMES = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo")
MONTH_NAMES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre")


THEMES = {
    "Espera": ("espera", "esperar", "tardaron", "tardo", "lento", "lentitud", "media hora", "demora", "cola"),
    "Comida": ("plato", "pizza", "pasta", "arroz", "carne", "frio", "fria", "crudo", "quemad", "salado", "soso", "recalentad", "sabor", "insipid"),
    "Trato": ("camarer", "trato", "borde", "maleducad", "antipat", "desagradable", "ignorad", "atencion", "personal"),
    "Reserva": ("reserva", "reservar", "telefono", "contestador", "cancel", "sin mesa", "confirmar"),
    "Precio": ("precio", "caro", "carisimo", "racion pequen", "calidad precio", "cobraron", "cobrar", "factura"),
    "Sala": ("ruido", "calor", "sucio", "olor", "bano", "limpieza", "terraza", "patio", "incomod"),
}

def normalize(text: str) -> str:
    text = unicodedata.normalize("NFD", text.casefold())
    return "".join(char for char in text if unicodedata.category(char) != "Mn")

def topic_counts(reviews):
    counts = {name: 0 for name in THEMES}
    unclassified = 0
    for review in reviews:
        text = normalize(review.get("text", ""))
        matched = False
        for name, terms in THEMES.items():
            if any(term in text for term in terms):
                counts[name] += 1
                matched = True
        if not matched:
            unclassified += 1
    return counts, unclassified

def star_counts(reviews):
    return [sum(review["rating"] == rating for review in reviews) for rating in range(1, 6)]

def normal_cdf(value: float) -> float:
    return 0.5 * (1 + math.erf(value / math.sqrt(2)))


def two_proportion_p(recent_bad: int, recent_n: int, prior_bad: int, prior_n: int):
    """Prueba Z bilateral agrupada; devuelve None si no hay dos grupos."""
    if not recent_n or not prior_n:
        return None
    pooled = (recent_bad + prior_bad) / (recent_n + prior_n)
    error = math.sqrt(pooled * (1 - pooled) * (1 / recent_n + 1 / prior_n))
    if error == 0:
        return 1.0
    z = (recent_bad / recent_n - prior_bad / prior_n) / error
    return 2 * (1 - normal_cdf(abs(z)))


def bucket(relative_time: str):
    value = relative_time.casefold().replace("\xa0", " ")
    value = value.replace("fecha de edición:", "").replace("fecha de edicion:", "").strip()
    # Las fuentes pueden contener «Hace» y «hace», pero no fechas absolutas.
    if "un mes" in value:
        return "base"
    if "4 semana" in value:
        return "4 semanas"
    if "3 semana" in value:
        return "3 semanas"
    if "2 semana" in value:
        return "2 semanas"
    if "una semana" in value or "1 semana" in value:
        return "1 semana"
    if "minuto" in value or "hora" in value:
        return "hoy"
    if "un día" in value or "un dia" in value:
        return "-1d"
    for days in range(2, 7):
        if f"{days} día" in value or f"{days} dia" in value:
            return f"-{days}d"
    raise ValueError(f"Marcador relativo no reconocido: {relative_time!r}")


def average(reviews):
    return round(sum(item["rating"] for item in reviews) / len(reviews), 2) if reviews else None


def timeline_labels(venues):
    captured_dates = {date.fromisoformat(venue["captured_at"][:10]) for venue in venues}
    if len(captured_dates) != 1:
        raise ValueError("Las capturas deben tener la misma fecha para etiquetar la serie")
    captured_at = captured_dates.pop()

    def full_day(day):
        return f"{WEEKDAY_NAMES[day.weekday()]} {day.day} de {MONTH_NAMES[day.month - 1]}"

    def short_day(day):
        return f"{WEEKDAY_NAMES[day.weekday()][:3]} {day.day} {MONTH_NAMES[day.month - 1][:3]}"

    labels = {}
    for days_ago, label in enumerate(("hoy", "-1d", "-2d", "-3d", "-4d", "-5d", "-6d")):
        day = captured_at - timedelta(days=days_ago)
        labels[label] = {"full": full_day(day), "short": short_day(day)}
    for weeks_ago, label in enumerate(("1 semana", "2 semanas", "3 semanas", "4 semanas"), start=1):
        end = captured_at - timedelta(days=weeks_ago * 7)
        start = end - timedelta(days=6)
        labels[label] = {
            "full": f"{start.day} - {end.day} de {MONTH_NAMES[end.month - 1]}",
            "short": f"{start.day}-{end.day} {MONTH_NAMES[end.month - 1][:3]}",
        }
    return labels


def venue_metrics(venue):
    reviews = venue["reviews"]
    recent, prior = reviews[:100], reviews[100:]
    recent_25 = reviews[:25]
    recent_bad = sum(review["rating"] <= 2 for review in recent)
    prior_bad = sum(review["rating"] <= 2 for review in prior)
    recent_topics, recent_unclassified = topic_counts([r for r in recent if r["rating"] <= 2])
    prior_topics, prior_unclassified = topic_counts([r for r in prior if r["rating"] <= 2])
    buckets = {name: [] for name in WEEKLY_ORDER + DAILY_ORDER}
    base = []
    for review in reviews:
        label = bucket(review["relative_time"])
        (base if label == "base" else buckets[label]).append(review)
    weekly_buckets = {**{name: buckets[name] for name in WEEKLY_ORDER[:-1]}, WEEKLY_ORDER[-1]: [review for name in DAILY_ORDER for review in buckets[name]]}
    weekly = [{"label": name, "n": len(weekly_buckets[name]), "rating": average(weekly_buckets[name])} for name in WEEKLY_ORDER]
    timeline = [{"label": name, "n": len(buckets[name]), "negative": sum(r["rating"] <= 2 for r in buckets[name]), "rating": average(buckets[name]), "reviews": [{"venue": APP_IDS[venue["id"]], "rating": r["rating"], "text": r.get("text", ""), "url": r.get("review_url", ""), "time": r.get("relative_time", "")} for r in buckets[name] if r["rating"] <= 2]} for name in TIMELINE_ORDER]
    p_value = two_proportion_p(recent_bad, len(recent), prior_bad, len(prior))
    if p_value is None:
        status, estado = "unknown", "Datos insuficientes"
    elif p_value < 0.05 and recent_bad / len(recent) > prior_bad / len(prior):
        status, estado = "critical", "Deterioro significativo"
    elif p_value < 0.05:
        status, estado = "improving", "Mejora significativa"
    else:
        status, estado = "no-signal", "Sin señal"
    return {
        "id": APP_IDS[venue["id"]],
        "rating": venue["rating"],
        "sample_n": len(reviews),
        "recent_100_rating": average(recent),
        "recent_25_rating": average(recent_25),
        "delta": round(average(recent) - venue["rating"], 2) if recent else None,
        "recent_bad": recent_bad,
        "recent_n": len(recent),
        "rest_bad": prior_bad,
        "rest_n": len(prior),
        "recent_bad_n": recent_bad,
        "rest_bad_n": prior_bad,
        "p_value": round(p_value, 6) if p_value is not None else None,
        "status": status,
        "estado": estado,
        "alert": status == "critical",
        "weekly": weekly,
        "timeline": timeline,
        "baseline": {"n": len(base), "rating": average(base)},
        "topics": {name: {"recent": recent_topics[name], "rest": prior_topics[name]} for name in THEMES},
        "unclassified": {"recent": recent_unclassified, "rest": prior_unclassified},
        "stars": {"recent_25": star_counts(recent_25), "recent_sample": star_counts(recent), "rest": star_counts(prior)},
    }


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    with SOURCE.open(encoding="utf-8") as source:
        venues = json.load(source)
    metrics = [venue_metrics(venue) for venue in venues]
    recent = [review for venue in venues for review in venue["reviews"][:100]]
    recent_25 = [review for venue in venues for review in venue["reviews"][:25]]
    prior = [review for venue in venues for review in venue["reviews"][100:]]
    all_reviews = [review for venue in venues for review in venue["reviews"]]
    recent_bad = [review for review in recent if review["rating"] <= 2]
    prior_bad = [review for review in prior if review["rating"] <= 2]
    recent_topics, recent_unclassified = topic_counts(recent_bad)
    prior_topics, prior_unclassified = topic_counts(prior_bad)
    group_timeline = []
    for label in TIMELINE_ORDER:
        bucket_reviews = [r for venue in venues for r in venue["reviews"] if bucket(r["relative_time"]) == label]
        group_timeline.append({"label": label, "n": len(bucket_reviews), "negative": sum(r["rating"] <= 2 for r in bucket_reviews), "rating": average(bucket_reviews), "reviews": [{"venue": next(APP_IDS[v["id"]] for v in venues if r in v["reviews"]), "rating": r["rating"], "text": r.get("text", ""), "url": r.get("review_url", ""), "time": r.get("relative_time", "")} for r in bucket_reviews if r["rating"] <= 2]})
    group = {
        "sample_n": len(all_reviews),
        "visible_n": sum(venue["total_reviews"] for venue in venues),
        "rating": average(all_reviews),
        "recent_100_rating": average(recent),
        "recent_25_rating": average(recent_25),
        "negative": sum(review["rating"] <= 2 for review in all_reviews),
        "negative_pct": round(sum(review["rating"] <= 2 for review in all_reviews) / len(all_reviews) * 100, 1),
        "alerts": sum(metric["alert"] for metric in metrics),
        "recent_100_n": len(recent),
        "recent_25_n": len(recent_25),
        "recent_bad_n": len(recent_bad),
        "rest_bad_n": len(prior_bad),
        "topics": {name: {"recent": recent_topics[name], "rest": prior_topics[name]} for name in THEMES},
        "unclassified": {"recent": recent_unclassified, "rest": prior_unclassified},
        "stars": {"recent_25": star_counts(recent_25), "recent_sample": star_counts(recent), "rest": star_counts(prior)},
        "timeline": group_timeline,
        "timeline_labels": timeline_labels(venues),
    }
    print(json.dumps({"venues": metrics, "group": group}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
