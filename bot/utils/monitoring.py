"""
monitoring.py - InstaShift
============================
Sistema de monitoreo Prometheus + Sentry para métricas y error tracking.
Se integra automáticamente en main.py sin cambios intrusivos.

Características:
- Contadores para posts publicados, logins, errores
- Métricas de duración de operaciones
- Health checks extensibles
- Sentry para error tracking en producción
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional

from prometheus_client import Counter, Gauge, Histogram, generate_latest

log = logging.getLogger(__name__)


# ── MÉTRICAS PROMETHEUS ───────────────────────────────────────────────────────

class InstaShiftMetrics:
    """Contenedor centralizado de métricas Prometheus para InstaShift."""

    def __init__(self) -> None:
        """Inicializa todas las métricas."""

        # Contadores
        self.posts_published = Counter(
            "instashift_posts_published_total",
            "Total de posts publicados en Discord",
            ["feed_name", "content_type"],
        )

        self.instagram_logins = Counter(
            "instashift_instagram_logins_total",
            "Total de intentos de login a Instagram",
            ["status"],  # success, failed, challenge, relogin_exceeded
        )

        self.instagram_api_calls = Counter(
            "instashift_instagram_api_calls_total",
            "Total de llamadas a API de Instagram",
            ["method", "status"],  # method: user_medias, user_info, etc | status: success, error, user_not_found
        )

        self.errors_total = Counter(
            "instashift_errors_total",
            "Total de errores por tipo y componente",
            ["error_type", "component"],
        )

        # Gauges (estado actual)
        self.active_feeds = Gauge(
            "instashift_active_feeds",
            "Número de feeds activos en este momento",
        )

        self.instagram_session_valid = Gauge(
            "instashift_instagram_session_valid",
            "¿La sesión de Instagram es válida? (0=no, 1=sí)",
        )

        self.last_check_timestamp = Gauge(
            "instashift_last_check_timestamp",
            "Timestamp del último health check",
        )

        # Histogramas (duraciones)
        self.feed_check_duration = Histogram(
            "instashift_feed_check_duration_seconds",
            "Duración del chequeo de feeds en segundos",
            ["feed_name"],
            buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0),
        )

        self.instagram_response_time = Histogram(
            "instashift_instagram_response_time_seconds",
            "Tiempo de respuesta de operaciones Instagram",
            ["method"],
            buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0),
        )

    def reset(self) -> None:
        """Reset de todas las métricas (útil para testing)."""
        # Los contadores no se pueden resetear, pero los gauges sí
        self.active_feeds.set(0)
        self.instagram_session_valid.set(0)
        self.last_check_timestamp.set(0)
        log.info("Métricas reseteadas")


# Instancia global de métricas
metrics = InstaShiftMetrics()


# ── HEALTH CHECKS ─────────────────────────────────────────────────────────────

class HealthCheck:
    """Sistema extensible de health checks."""

    def __init__(self) -> None:
        self._checks: Dict[str, tuple[Callable, bool]] = {}

    def register_check(
        self,
        name: str,
        check_func: Callable,
        critical: bool = False,
    ) -> None:
        """
        Registra un nuevo health check.

        Args:
            name: Nombre del check
            check_func: Función async que retorna True/False
            critical: Si False, el bot es "unhealthy" si falla este check
        """
        self._checks[name] = (check_func, critical)
        log.debug(f"[HealthCheck] Registrado: {name} (critical={critical})")

    async def run_all_checks(self) -> Dict[str, Any]:
        """Ejecuta todos los checks registrados y retorna los resultados."""
        results = {}
        all_ok = True

        for name, (check_func, is_critical) in self._checks.items():
            try:
                status = await check_func() if callable(check_func) else check_func
                results[name] = {
                    "status": "ok" if status else "failed",
                    "critical": is_critical,
                }
                if not status and is_critical:
                    all_ok = False
            except Exception as e:
                log.error(f"[HealthCheck] Error en {name}: {e}")
                results[name] = {
                    "status": "error",
                    "critical": is_critical,
                    "error": str(e),
                }
                if is_critical:
                    all_ok = False

        # Actualizar métrica
        metrics.last_check_timestamp.set(datetime.now(timezone.utc).timestamp())

        return {
            "status": "healthy" if all_ok else "unhealthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks": results,
        }


# Instancia global de health checks
health_check = HealthCheck()


# ── ERROR TRACKING (SENTRY) ───────────────────────────────────────────────────

def record_error(
    error_type: str,
    component: str,
    error: Exception,
) -> None:
    """
    Registra un error en métricas y opcionalmente en Sentry.

    Args:
        error_type: Tipo de error (ej: "user_not_found")
        component: Componente donde ocurrió (ej: "instagram")
        error: La excepción
    """
    # Incrementar métrica de errores
    metrics.errors_total.labels(error_type=error_type, component=component).inc()

    # Log del error
    log.error(f"[{component}] {error_type}: {error}")

    # Sentry (si está configurado)
    try:
        import sentry_sdk

        if sentry_sdk.Hub.current.client:
            sentry_sdk.capture_exception(error)
    except Exception:
        pass  # Sentry no disponible


# ── ENDPOINT PROMETHEUS ───────────────────────────────────────────────────────

def get_metrics_text() -> str:
    """
    Retorna las métricas en formato Prometheus (text/plain).

    Uso:
        curl http://localhost:8000/metrics
    """
    return generate_latest().decode("utf-8")