"""
feeds.py – InstaShift
=======================
Comandos de slash para gestionar feeds de Instagram.

Comandos disponibles
--------------------
/feed add    – Agregar un nuevo feed de Instagram
/feed list   – Listar todos los feeds activos
/feed remove – Eliminar un feed
/feed pause  – Pausar un feed temporalmente
/feed resume – Reanudar un feed pausado
"""

from __future__ import annotations

import logging
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from bot.database import add_feed, remove_feed, pause_feed, resume_feed, get_feeds

# ── Logger del módulo ─────────────────────────────────────────────────────────
log = logging.getLogger(__name__)

# ── Paleta de colores para embeds ─────────────────────────────────────────────
FEED_COLOR = 0x5865F2
SUCCESS_COLOR = 0x00B06B
ERROR_COLOR = 0xFF4444
INFO_COLOR = 0x5865F2


# ══════════════════════════════════════════════════════════════════════════════
# Cog de gestión de feeds
# ══════════════════════════════════════════════════════════════════════════════

class FeedsCog(commands.Cog, name="Feeds"):
    """Comandos slash para gestionar feeds de Instagram."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # ── Grupo de comandos /feed ────────────────────────────────────────────────

    feed_group = app_commands.Group(
        name="feed",
        description="Comandos para gestionar feeds de Instagram"
    )

    # ── /feed add ──────────────────────────────────────────────────────────────

    @feed_group.command(
        name="add",
        description="Agregar un nuevo feed de Instagram",
    )
    @app_commands.describe(
        cuenta="Nombre de la cuenta de Instagram a seguir (sin @)",
        canal="Canal de Discord donde publicar los posts",
        hilo="(Opcional) Hilo específico del canal",
        rol="(Opcional) Rol a mencionar en las publicaciones",
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def feed_add(
        self,
        interaction: discord.Interaction,
        cuenta: str,
        canal: discord.TextChannel,
        hilo: Optional[discord.Thread] = None,
        rol: Optional[discord.Role] = None,
    ) -> None:
        """Agrega un nuevo feed de Instagram."""
        await interaction.response.defer(ephemeral=True)

        cuenta = cuenta.strip().lower()
        if not cuenta:
            await interaction.followup.send(
                "❌ El nombre de la cuenta no puede estar vacío.", ephemeral=True
            )
            return

        # Agregar feed a la base de datos
        feed_id = await add_feed(
            guild_id=interaction.guild_id,
            instagram_account=cuenta,
            channel_id=canal.id,
            thread_id=hilo.id if hilo else None,
            role_id=rol.id if rol else None,
        )

        if feed_id:
            embed = discord.Embed(
                title="✅ Feed agregado",
                description=(
                    f"El feed de **@{cuenta}** ha sido agregado.\n"
                    f"Canal: {canal.mention}\n"
                    f"Feed ID: `#{feed_id}`"
                ),
                color=SUCCESS_COLOR,
            )
        else:
            embed = discord.Embed(
                title="❌ Error al agregar feed",
                description=f"El feed de **@{cuenta}** ya existe en este canal.",
                color=ERROR_COLOR,
            )

        await interaction.followup.send(embed=embed, ephemeral=True)

        # Log de estadísticas
        from bot.database import log_stat_command
        await log_stat_command(interaction.guild_id, "feed add")

    # ── /feed list ─────────────────────────────────────────────────────────────

    @feed_group.command(
        name="list",
        description="Listar todos los feeds activos del servidor",
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def feed_list(self, interaction: discord.Interaction) -> None:
        """Lista todos los feeds activos."""
        await interaction.response.defer(ephemeral=True)

        feeds = await get_feeds(interaction.guild_id)

        if not feeds:
            await interaction.followup.send(
                "📭 No hay feeds activos en este servidor.",
                ephemeral=True,
            )
            return

        # Formatear lista de feeds
        lineas = []
        for feed in feeds:
            canal = self.bot.get_channel(feed['channel_id'])
            canal_name = canal.mention if canal else f"(Canal #{feed['channel_id']})"
            lineas.append(
                f"**#{feed['id']}** - **@{feed['ig_account']}** → {canal_name}"
            )

        embed = discord.Embed(
            title="📸 Feeds activos",
            description="\n".join(lineas),
            color=FEED_COLOR,
        )
        embed.set_footer(text="Usa /feed remove <id> para eliminar un feed.")

        await interaction.followup.send(embed=embed, ephemeral=True)

        # Log de estadísticas
        from bot.database import log_stat_command
        await log_stat_command(interaction.guild_id, "feed list")

    # ── /feed remove ───────────────────────────────────────────────────────────

    @feed_group.command(
        name="remove",
        description="Eliminar un feed",
    )
    @app_commands.describe(
        feed_id="ID del feed a eliminar (obtén la lista con /feed list)",
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def feed_remove(
        self,
        interaction: discord.Interaction,
        feed_id: int,
    ) -> None:
        """Elimina un feed."""
        await interaction.response.defer(ephemeral=True)

        # Obtener el feed para verificar que existe
        feeds = await get_feeds(interaction.guild_id)
        feed = next((f for f in feeds if f['id'] == feed_id), None)

        if not feed:
            embed = discord.Embed(
                title="❌ Feed no encontrado",
                description=f"No existe un feed con ID **{feed_id}** en este servidor.",
                color=ERROR_COLOR,
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # Eliminar el feed
        eliminado = await remove_feed(
            guild_id=interaction.guild_id,
            instagram_account=feed['ig_account'],
            channel_id=feed['channel_id'],
        )

        if eliminado:
            embed = discord.Embed(
                title="🗑️ Feed eliminado",
                description=f"El feed **@{feed['ig_account']}** ha sido eliminado.",
                color=SUCCESS_COLOR,
            )
        else:
            embed = discord.Embed(
                title="⚠️ Error al eliminar",
                description="No se pudo eliminar el feed.",
                color=INFO_COLOR,
            )

        await interaction.followup.send(embed=embed, ephemeral=True)

        # Log de estadísticas
        from bot.database import log_stat_command
        await log_stat_command(interaction.guild_id, "feed remove")

    # ── /feed pause ────────────────────────────────────────────────────────────

    @feed_group.command(
        name="pause",
        description="Pausar un feed temporalmente",
    )
    @app_commands.describe(
        feed_id="ID del feed a pausar",
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def feed_pause(
        self,
        interaction: discord.Interaction,
        feed_id: int,
    ) -> None:
        """Pausa un feed."""
        await interaction.response.defer(ephemeral=True)

        pausado = await pause_feed(feed_id)

        if pausado:
            embed = discord.Embed(
                title="⏸️ Feed pausado",
                description=f"El feed **#{feed_id}** ha sido pausado.",
                color=INFO_COLOR,
            )
        else:
            embed = discord.Embed(
                title="❌ Feed no encontrado",
                description=f"No existe un feed con ID **{feed_id}**.",
                color=ERROR_COLOR,
            )

        await interaction.followup.send(embed=embed, ephemeral=True)

        # Log de estadísticas
        from bot.database import log_stat_command
        await log_stat_command(interaction.guild_id, "feed pause")

    # ── /feed resume ───────────────────────────────────────────────────────────

    @feed_group.command(
        name="resume",
        description="Reanudar un feed pausado",
    )
    @app_commands.describe(
        feed_id="ID del feed a reanudar",
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def feed_resume(
        self,
        interaction: discord.Interaction,
        feed_id: int,
    ) -> None:
        """Reanuda un feed pausado."""
        await interaction.response.defer(ephemeral=True)

        reanudado = await resume_feed(feed_id)

        if reanudado:
            embed = discord.Embed(
                title="▶️ Feed reanudado",
                description=f"El feed **#{feed_id}** ha sido reanudado.",
                color=SUCCESS_COLOR,
            )
        else:
            embed = discord.Embed(
                title="❌ Feed no encontrado",
                description=f"No existe un feed con ID **{feed_id}**.",
                color=ERROR_COLOR,
            )

        await interaction.followup.send(embed=embed, ephemeral=True)

        # Log de estadísticas
        from bot.database import log_stat_command
        await log_stat_command(interaction.guild_id, "feed resume")

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

        if interaction.response.is_done():
            await interaction.followup.send(msg, ephemeral=True)
        else:
            await interaction.response.send_message(msg, ephemeral=True)


# ── Función de configuración del cog ──────────────────────────────────────────

async def setup(bot: commands.Bot) -> None:
    """Registra el cog en el bot. Llamada automáticamente por load_extension()."""
    await bot.add_cog(FeedsCog(bot))
    # Registrar el command group en el árbol de comandos
    bot.tree.add_command(FeedsCog.feed_group)
