"""
feeds.py – InstaShift
======================
Comandos de slash para gestionar suscripciones de feeds de Instagram.

Comandos disponibles
--------------------
/feed add     – Suscribir un canal a una cuenta de Instagram
/feed list    – Ver los feeds activos en este servidor
/feed remove  – Eliminar una suscripción
/feed pause   – Pausar temporalmente un feed
/feed resume  – Reanudar un feed pausado
/dashboard    – Vista general rica con todos los feeds
/checknow     – Forzar una verificación inmediata de feeds
/sync         – Re-sincronizar comandos slash (admin)
/sync clear   – Eliminar todos los comandos slash (admin)
"""

from __future__ import annotations

import logging
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from bot.database import add_feed, get_feeds, remove_feed

# ── Logger del módulo ─────────────────────────────────────────────────────────
log = logging.getLogger(__name__)

# ── Paleta de colores para embeds ─────────────────────────────────────────────
IG_COLOR = 0xE1306C      # Rosa Instagram
SUCCESS_COLOR = 0x00B06B  # Verde éxito
ERROR_COLOR = 0xFF4444    # Rojo error
INFO_COLOR = 0x5865F2     # Azul Discord


def _formatear_feed(idx: int, feed: dict) -> str:
    """
    Formatea una fila de feed para mostrarla en /list o /dashboard.
    Ejemplo: 1. @nasa → #general | @Noticias
    """
    canal = f"<#{feed['channel_id']}>"
    hilo = f" → <#{feed['thread_id']}>" if feed.get("thread_id") else ""
    rol = f"  |  <@&{feed['role_id']}>" if feed.get("role_id") else ""
    return (
        f"**{idx}.** "
        f"[@{feed['instagram_account']}](https://instagram.com/{feed['instagram_account']}) "
        f"{canal}{hilo}{rol}"
    )


# ══════════════════════════════════════════════════════════════════════════════
# Cog de gestión de feeds
# ══════════════════════════════════════════════════════════════════════════════

class FeedsCog(commands.Cog, name="Feeds"):
    """Comandos slash para gestionar suscripciones de Instagram → Discord."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # ── Grupo de comandos /feed ───────────────────────────────────────────────

    feed_group = app_commands.Group(name="feed", description="Comandos para gestionar feeds de Instagram")

    # ── /feed add ─────────────────────────────────────────────────────────────

    @feed_group.command(
        name="add",
        description="Suscribir un canal a las publicaciones de una cuenta de Instagram.",
    )
    @app_commands.describe(
        cuenta="Usuario de Instagram a seguir (sin @)",
        canal="Canal de Discord donde se publicarán las actualizaciones (por defecto: canal actual)",
        hilo="Hilo opcional donde publicar en lugar del canal",
        rol="Rol opcional para mencionar en cada nueva publicación",
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def feed_add(
        self,
        interaction: discord.Interaction,
        cuenta: str,
        canal: Optional[discord.TextChannel] = None,
        hilo: Optional[discord.Thread] = None,
        rol: Optional[discord.Role] = None,
    ) -> None:
        """Agrega una nueva suscripción al feed de Instagram especificado."""
        await interaction.response.defer(ephemeral=True)

        # Limpiar y normalizar la cuenta
        cuenta = cuenta.lstrip("@").strip().lower()
        if not cuenta:
            await interaction.followup.send("❌ El nombre de usuario no es válido.", ephemeral=True)
            return

        # Determinar el canal de destino
        target_channel = canal or interaction.channel
        if not isinstance(target_channel, (discord.TextChannel, discord.Thread)):
            await interaction.followup.send(
                "❌ Por favor selecciona un canal de texto válido.", ephemeral=True
            )
            return

        # Insertar la suscripción en la base de datos
        feed_id = await add_feed(
            guild_id=interaction.guild_id,
            instagram_account=cuenta,
            channel_id=target_channel.id,
            thread_id=hilo.id if hilo else None,
            role_id=rol.id if rol else None,
        )

        if not feed_id:
            # La combinación ya existe (restricción UNIQUE en la BD)
            await interaction.followup.send(
                f"⚠️ **@{cuenta}** ya está siendo seguido en {target_channel.mention}.",
                ephemeral=True,
            )
            return

        # Construir embed de confirmación
        embed = discord.Embed(
            title="✅ Feed agregado",
            color=SUCCESS_COLOR,
            description=(
                f"Ahora siguiendo **[@{cuenta}](https://instagram.com/{cuenta})**\n"
                f"Las publicaciones aparecerán en {target_channel.mention}"
                + (f" → {hilo.mention}" if hilo else "")
                + (f"\nMención: {rol.mention}" if rol else "")
            ),
        )
        embed.set_footer(text="Las actualizaciones se verifican cada 10 minutos.")

        await interaction.followup.send(embed=embed, ephemeral=True)
        log.info(
            "[Feeds] Servidor %s: nuevo feed @%s → canal %s",
            interaction.guild_id, cuenta, target_channel.id,
        )

        # Log de estadísticas
        from bot.database import log_stat_command
        await log_stat_command(interaction.guild_id, "feed add")

    # ── /feed remove ──────────────────────────────────────────────────────────

    @feed_group.command(
        name="remove",
        description="Dejar de seguir una cuenta de Instagram en un canal.",
    )
    @app_commands.describe(
        cuenta="Usuario de Instagram a dejar de seguir (sin @)",
        canal="Canal del que se elimina la suscripción (por defecto: canal actual)",
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def feed_remove(
        self,
        interaction: discord.Interaction,
        cuenta: str,
        canal: Optional[discord.TextChannel] = None,
    ) -> None:
        """Elimina una suscripción de feed existente."""
        await interaction.response.defer(ephemeral=True)

        cuenta = cuenta.lstrip("@").strip().lower()
        target_channel = canal or interaction.channel

        # Eliminar de la base de datos
        eliminado = await remove_feed(
            guild_id=interaction.guild_id,
            instagram_account=cuenta,
            channel_id=target_channel.id,
        )

        if eliminado:
            embed = discord.Embed(
                title="🗑️ Feed eliminado",
                description=(
                    f"Se dejó de seguir **@{cuenta}** en {target_channel.mention}.\n"
                    "Las publicaciones anteriores no serán eliminadas."
                ),
                color=ERROR_COLOR,
            )
        else:
            embed = discord.Embed(
                title="⚠️ Feed no encontrado",
                description=(
                    f"No hay un feed activo de **@{cuenta}** "
                    f"en {target_channel.mention}.\n"
                    "Usa **/feed list** para ver los feeds activos."
                ),
                color=INFO_COLOR,
            )

        await interaction.followup.send(embed=embed, ephemeral=True)

        # Log de estadísticas
        from bot.database import log_stat_command
        await log_stat_command(interaction.guild_id, "feed remove")

    # ── /feed list ────────────────────────────────────────────────────────────

    @feed_group.command(
        name="list",
        description="Ver todos los feeds activos de Instagram en este servidor.",
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def feed_list(self, interaction: discord.Interaction) -> None:
        """Muestra la lista compacta de todos los feeds activos en el servidor."""
        await interaction.response.defer(ephemeral=True)

        feeds = await get_feeds(interaction.guild_id)
        if not feeds:
            await interaction.followup.send(
                "📭 No hay feeds activos.\nUsa **/feed add** para agregar uno.",
                ephemeral=True,
            )
            return

        # Formatear cada feed como una línea
        lineas = [_formatear_feed(i + 1, f) for i, f in enumerate(feeds)]

        embed = discord.Embed(
            title=f"📋 Feeds activos ({len(feeds)})",
            description="\n".join(lineas),
            color=IG_COLOR,
        )
        embed.set_footer(text="Usa /feed remove para eliminar un feed.")

        await interaction.followup.send(embed=embed, ephemeral=True)

        # Log de estadísticas
        from bot.database import log_stat_command
        await log_stat_command(interaction.guild_id, "feed list")

    # ── /feed pause ───────────────────────────────────────────────────────────

    @feed_group.command(
        name="pause",
        description="Pausar temporalmente un feed (sin eliminar).",
    )
    @app_commands.describe(
        feed_id="ID del feed a pausar (obtén la lista con /feed list)",
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def feed_pause(
        self,
        interaction: discord.Interaction,
        feed_id: int,
    ) -> None:
        """Pausa un feed sin eliminarlo."""
        await interaction.response.defer(ephemeral=True)

        from bot.database import pause_feed

        pausado = await pause_feed(feed_id)

        if pausado:
            embed = discord.Embed(
                title="⏸️ Feed pausado",
                description=f"El feed **#{feed_id}** ha sido pausado.\nUsa **/feed resume** para reactivarlo.",
                color=INFO_COLOR,
            )
        else:
            embed = discord.Embed(
                title="⚠️ Feed no encontrado",
                description=f"No existe un feed con ID **{feed_id}**.",
                color=ERROR_COLOR,
            )

        await interaction.followup.send(embed=embed, ephemeral=True)

        # Log de estadísticas
        from bot.database import log_stat_command
        await log_stat_command(interaction.guild_id, "feed pause")

    # ── /feed resume ──────────────────────────────────────────────────────────

    @feed_group.command(
        name="resume",
        description="Reanudar un feed pausado.",
    )
    @app_commands.describe(
        feed_id="ID del feed a reanudar (obtén la lista con /feed list)",
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def feed_resume(
        self,
        interaction: discord.Interaction,
        feed_id: int,
    ) -> None:
        """Reanuda un feed pausado."""
        await interaction.response.defer(ephemeral=True)

        from bot.database import resume_feed

        reanudado = await resume_feed(feed_id)

        if reanudado:
            embed = discord.Embed(
                title="▶️ Feed reanudado",
                description=f"El feed **#{feed_id}** está activo nuevamente.",
                color=SUCCESS_COLOR,
            )
        else:
            embed = discord.Embed(
                title="⚠️ Feed no encontrado",
                description=f"No existe un feed con ID **{feed_id}**.",
                color=ERROR_COLOR,
            )

        await interaction.followup.send(embed=embed, ephemeral=True)

        # Log de estadísticas
        from bot.database import log_stat_command
        await log_stat_command(interaction.guild_id, "feed resume")

    # ── /dashboard ────────────────────────────────────────────────────────────

    @app_commands.command(
        name="dashboard",
        description="Panel de control con la vista general de los feeds de Instagram.",
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def dashboard(self, interaction: discord.Interaction) -> None:
        """Vista rica con todos los feeds activos del servidor, visible para todos."""
        await interaction.response.defer(ephemeral=False)

        feeds = await get_feeds(interaction.guild_id)
        guild = interaction.guild

        embed = discord.Embed(
            title="📊 Panel de control – InstaShift",
            color=IG_COLOR,
        )

        # Miniatura del servidor si tiene icono
        if guild and guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        if not feeds:
            embed.description = (
                "No hay suscripciones activas en este servidor.\n"
                "Usa **/follow** para comenzar a seguir cuentas de Instagram."
            )
        else:
            plural = "suscripciones" if len(feeds) != 1 else "suscripción"
            embed.description = (
                f"**{len(feeds)} {plural}** activas en "
                f"**{guild.name if guild else 'este servidor'}**."
            )

            # Agregar cada feed como un campo del embed
            for feed in feeds:
                canal = f"<#{feed['channel_id']}>"
                hilo = f" → <#{feed['thread_id']}>" if feed.get("thread_id") else ""
                rol = f"\n📢 Mención: <@&{feed['role_id']}>" if feed.get("role_id") else ""
                ultimo = feed.get("last_media_id") or "—"

                embed.add_field(
                    name=f"📸 @{feed['instagram_account']}",
                    value=(
                        f"Canal: {canal}{hilo}{rol}\n"
                        f"Último visto: `{ultimo[:20]}`"
                    ),
                    inline=True,
                )

        embed.set_footer(
            text="Las actualizaciones se verifican cada 10 minutos  •  /checknow para verificar ahora"
        )

        await interaction.followup.send(embed=embed)

    # ── /checknow ─────────────────────────────────────────────────────────────

    @app_commands.command(
        name="checknow",
        description="Forzar una verificación inmediata de todos los feeds de Instagram.",
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def checknow(self, interaction: discord.Interaction) -> None:
        """Ejecuta el loop de feeds de forma manual sin esperar al intervalo."""
        await interaction.response.defer(ephemeral=True)

        # Obtener el cog del scraper para ejecutar su loop manualmente
        scraper_cog = self.bot.cogs.get("Instagram")
        if scraper_cog is None:
            await interaction.followup.send(
                "❌ El módulo de scraping no está cargado. Reinicia el bot.",
                ephemeral=True,
            )
            return

        await interaction.followup.send(
            "🔄 Verificando feeds ahora… Los resultados aparecerán en sus canales correspondientes.",
            ephemeral=True,
        )

        # Lanzar el loop como tarea asíncrona para no bloquear el hilo principal
        self.bot.loop.create_task(scraper_cog.feed_loop())  # type: ignore[attr-defined]

    # ── /sync ─────────────────────────────────────────────────────────────────

    @app_commands.command(
        name="sync",
        description="[Admin] Sincronizar comandos slash. Usa 'clear' para eliminarlos todos.",
    )
    @app_commands.describe(
        mode="Dejar vacío para sincronizar, escribir 'clear' para eliminar todos los comandos."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def sync(
        self,
        interaction: discord.Interaction,
        mode: Optional[str] = None,
    ) -> None:
        """Sincroniza o limpia los comandos slash del servidor."""
        await interaction.response.defer(ephemeral=True)

        if mode and mode.strip().lower() == "clear":
            # Eliminar todos los comandos del servidor actual
            self.bot.tree.clear_commands(guild=interaction.guild)
            await self.bot.tree.sync(guild=interaction.guild)
            await interaction.followup.send(
                "🧹 Todos los comandos del servidor fueron eliminados.\n"
                "Los comandos globales pueden tardar hasta 1 hora en actualizarse.",
                ephemeral=True,
            )
            return

        # Sincronización inteligente: primero el servidor, luego global
        synced_guild = await self.bot.tree.sync(guild=interaction.guild)
        synced_global = await self.bot.tree.sync()

        await interaction.followup.send(
            f"✅ Sincronizados **{len(synced_guild)}** comandos de servidor y "
            f"**{len(synced_global)}** comandos globales.",
            ephemeral=True,
        )
        log.info(
            "[Sync] %d servidor + %d global sincronizados por %s",
            len(synced_guild), len(synced_global), interaction.user,
        )

    # ── Manejador global de errores del cog ───────────────────────────────────

    async def cog_app_command_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ) -> None:
        """Captura y responde a errores de comandos slash de forma amigable."""
        if isinstance(error, app_commands.MissingPermissions):
            msg = "❌ Necesitas el permiso **Gestionar servidor** para usar este comando."
        elif isinstance(error, app_commands.CommandOnCooldown):
            msg = f"⏳ Comando en cooldown. Intenta de nuevo en {error.retry_after:.1f}s."
        elif isinstance(error, app_commands.BotMissingPermissions):
            msg = "❌ Me faltan permisos necesarios en este canal para ejecutar el comando."
        else:
            log.exception("Error no manejado en comando slash: %s", error)
            msg = f"❌ Ocurrió un error inesperado: `{error}`"

        # Responder según si la interacción ya fue respondida o no
        if interaction.response.is_done():
            await interaction.followup.send(msg, ephemeral=True)
        else:
            await interaction.response.send_message(msg, ephemeral=True)


# ── Función de configuración del cog ──────────────────────────────────────────

async def setup(bot: commands.Bot) -> None:
    """Registra el cog en el bot. Llamada automáticamente por load_extension()."""
    cog = FeedsCog(bot)
    # Registrar el grupo de comandos /feed
    bot.tree.add_command(cog.feed_group)
    await bot.add_cog(cog)
