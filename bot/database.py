"""
database.py – InstaSwift
========================
Capa de acceso a datos usando MySQL asíncrono (aiomysql).

Se conecta a la base de datos del panel web en Hostinger.

Tablas usadas
-------------
instaswift_feeds        : suscripciones gestionadas desde el panel web
instaswift_posted_media : registro anti-duplicados (se crea si no existe)
instaswift_stats_posts  : estadísticas de publicaciones
instaswift_stats_commands: estadísticas de comandos usados
"""

from __future__ import annotations

import logging
import os
from typing import Optional

import aiomysql

# ── Logger del módulo ─────────────────────────────────────────────────────────
log = logging.getLogger(__name__)

# ── Variables de conexión MySQL ────────────────────────────────────────────────
DB_HOST: str = os.getenv("DB_HOST", "auth-db1439.hstgr.io")
DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
DB_USER: str = os.getenv("DB_USER", "u670415175_instaswift")
DB_PASS: str = os.getenv("DB_PASS", "")
DB_NAME: str = os.getenv("DB_NAME", "u670415175_instaswift")

# Pool global de conexiones (se inicializa en init_db)
_pool: Optional[aiomysql.Pool] = None


# ══════════════════════════════════════════════════════════════════════════════
# Inicialización
# ══════════════════════════════════════════════════════════════════════════════

async def init_db() -> None:
    """
    Crea el pool de conexiones MySQL y asegura que la tabla
    instaswift_posted_media exista (anti-duplicados del bot).
    Se llama una vez en setup_hook() de main.py.
    """
    global _pool

    log.info("[DB] Conectando a MySQL %s:%s / %s ...", DB_HOST, DB_PORT, DB_NAME)
    _pool = await aiomysql.create_pool(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        db=DB_NAME,
        charset="utf8mb4",
        autocommit=True,
        minsize=1,
        maxsize=5,
        echo=False,
    )

    # Crear tabla anti-duplicados si el panel web no la creó
    async with _pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS instaswift_posted_media (
                    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                    feed_id     INT UNSIGNED NOT NULL,
                    media_id    VARCHAR(100) NOT NULL,
                    posted_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY uq_feed_media (feed_id, media_id),
                    INDEX idx_feed_id (feed_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

    log.info("[DB] MySQL listo. Pool creado (min=1, max=5).")


async def close_db() -> None:
    """Cierra el pool de conexiones al apagar el bot."""
    global _pool
    if _pool:
        _pool.close()
        await _pool.wait_closed()
        _pool = None
        log.info("[DB] Pool MySQL cerrado.")


def _get_pool() -> aiomysql.Pool:
    """Helper: lanza error claro si el pool no fue inicializado."""
    if _pool is None:
        raise RuntimeError("DB pool no inicializado. Llama a init_db() primero.")
    return _pool


# ══════════════════════════════════════════════════════════════════════════════
# Lectura de feeds (desde el panel web)
# ══════════════════════════════════════════════════════════════════════════════

async def get_all_active_feeds() -> list[dict]:
    """
    Retorna todos los feeds activos de todos los servidores.
    Lee directamente de instaswift_feeds (gestionada por el panel web).

    Columnas devueltas:
    id, guild_id, ig_account, channel_id, content_type, active
    """
    async with _get_pool().acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                """SELECT id, guild_id, ig_account, channel_id, content_type, active
                   FROM instaswift_feeds
                   WHERE active = 1
                   ORDER BY guild_id, id"""
            )
            return await cur.fetchall()


async def get_feeds(guild_id: int) -> list[dict]:
    """
    Retorna los feeds activos de un servidor específico.
    Usado por /list y /dashboard.
    """
    async with _get_pool().acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                """SELECT id, guild_id, ig_account, channel_id, content_type, active, created_at
                   FROM instaswift_feeds
                   WHERE guild_id = %s AND active = 1
                   ORDER BY id""",
                (guild_id,),
            )
            return await cur.fetchall()


async def update_last_media_id(feed_id: int, media_id: str) -> None:
    """
    No-op compatible: la BD del panel no tiene campo last_media_id.
    El anti-duplicados real se gestiona con instaswift_posted_media.
    Se mantiene esta firma para no romper las llamadas existentes del scraper.
    """
    pass


# ══════════════════════════════════════════════════════════════════════════════
# Anti-duplicados (tabla del bot en la misma BD MySQL)
# ══════════════════════════════════════════════════════════════════════════════

async def is_already_posted(feed_id: int, media_id: str) -> bool:
    """
    Verifica si un contenido ya fue publicado en Discord para este feed.
    Consulta instaswift_posted_media en la BD MySQL.
    """
    async with _get_pool().acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT 1 FROM instaswift_posted_media WHERE feed_id=%s AND media_id=%s",
                (feed_id, media_id),
            )
            return await cur.fetchone() is not None


async def mark_as_posted(feed_id: int, media_id: str) -> None:
    """
    Registra que un contenido fue publicado. Ignora duplicados (INSERT IGNORE).
    """
    async with _get_pool().acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """INSERT IGNORE INTO instaswift_posted_media (feed_id, media_id)
                   VALUES (%s, %s)""",
                (feed_id, media_id),
            )


# ══════════════════════════════════════════════════════════════════════════════
# Estadísticas
# ══════════════════════════════════════════════════════════════════════════════

async def log_stat_post(guild_id: int, feed_id: int, media_type_int: int) -> None:
    """
    Registra una publicación en instaswift_stats_posts.

    Convierte el media_type numérico de instagrapi al enum del panel:
      1 (foto/post)  → 'post'
      2 (video/reel) → 'reel'
      8 (álbum)      → 'post'
    """
    tipo = "reel" if media_type_int == 2 else "post"
    async with _get_pool().acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """INSERT INTO instaswift_stats_posts (guild_id, feed_id, content_type)
                   VALUES (%s, %s, %s)""",
                (guild_id, feed_id, tipo),
            )


async def log_stat_command(guild_id: int, command_name: str) -> None:
    """
    Registra el uso de un comando slash en instaswift_stats_commands.
    """
    async with _get_pool().acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """INSERT INTO instaswift_stats_commands (guild_id, command_name)
                   VALUES (%s, %s)""",
                (guild_id, command_name),
            )
