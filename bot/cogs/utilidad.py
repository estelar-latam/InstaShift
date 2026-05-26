"""
utilidad.py – InstaShift
========================
Comandos de utilidad e información del bot.

Comandos disponibles
--------------------
/ayuda – Muestra la lista de comandos disponibles y enlace a documentación
/plan  – Muestra el plan del servidor y límites de uso
/stats – Estadísticas de publicaciones y comandos usados
"""

from __future__ import annotations

import logging

import discord
from discord import app_commands
from discord.ext import commands

from bot.database import get_feeds, get_stats_posts, get_stats_commands

# ── Logger del módulo ─────────────────────────────────────────────────────────
log = logging.getLogger(__name__)

# ── Paleta de colores para embeds ─────────────────────────────────────────────
INFO_COLOR = 0x5865F2
SUCCESS_COLOR = 0x00B06B


class UtilidadCog(commands.Cog, name="Utilidad"):
    """Comandos de utilidad e información."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # ── /ayuda ─────────────────────────────────────────────────────────────────

    @app_commands.command(
        name="ayuda",
        description="Muestra la lista de comandos disponibles y enlace a documentación.",
    )
    async def ayuda(self, interaction: discord.Interaction) -> None:
        """Muestra información de ayuda y documentación."""
        await interaction.response.defer(ephemeral=True)

        embed = discord.Embed(
            title="📚 Centro de Ayuda – InstaSwift",
            description="Aquí están todos los comandos disponibles.",
            color=INFO_COLOR,
        )

        embed.add_field(
            name="📸 Comandos de feeds",
            value=(
                "`/feed add` – Agregar un nuevo feed\n"
                "`/feed list` – Ver feeds activos\n"
                "`/feed remove` – Eliminar un feed\n"
                "`/feed pause` – Pausar un feed\n"
                "`/feed resume` – Reanudar un feed"
            ),
            inline=False,
        )

        embed.add_field(
            name="🔍 Comandos de filtros",
            value=(
                "`/filtro add` – Agregar filtro a un feed\n"
                "`/filtro list` – Ver filtros de un feed\n"
                "`/filtro remove` – Eliminar un filtro"
            ),
            inline=False,
        )

        embed.add_field(
            name="ℹ️ Comandos de información",
            value=(
                "`/plan` – Ver el plan actual del servidor\n"
                "`/stats` – Ver estadísticas de publicaciones\n"
                "`/ayuda` – Esta página"
            ),
            inline=False,
        )

        embed.add_field(
            name="📖 Documentación completa",
            value="Visita https://estelarlatam.com/plataforma/instaswift/documentacion/",
            inline=False,
        )

        embed.set_footer(text="InstaSwift v2.0 • Espejar Instagram en Discord")

        await interaction.followup.send(embed=embed, ephemeral=True)

        # Log de estadísticas
        from bot.database import log_stat_command
        await log_stat_command(interaction.guild_id, "ayuda")

    # ── /plan ──────────────────────────────────────────────────────────────────

    @app_commands.command(
        name="plan",
        description="Ver el plan actual del servidor y límites de uso.",
    )
    async def plan(self, interaction: discord.Interaction) -> None:
        """Muestra información del plan del servidor."""
        await interaction.response.defer(ephemeral=True)

        feeds = await get_feeds(interaction.guild_id)
        feed_count = len(feeds)

        embed = discord.Embed(
            title="📊 Plan del servidor",
            color=SUCCESS_COLOR,
        )

        # Plan actual (por defecto Free)
        plan_type = "Free"
        max_feeds = 5
        max_filters = 0

        embed.add_field(
            name="Plan actual",
            value=f"**{plan_type}**",
            inline=True,
        )

        embed.add_field(
            name="Feeds usados",
            value=f"**{feed_count}** / {max_feeds}",
            inline=True,
        )

        embed.add_field(
            name="Funcionalidades",
            value=(
                "✅ Feeds ilimitados por servidor\n"
                "❌ Filtros avanzados (PRO)\n"
                "✅ Estadísticas (últimos 7 días)\n"
                "✅ Soporte comunitario"
            ),
            inline=False,
        )

        embed.set_footer(text="Actualiza a PRO para desbloquear más funcionalidades.")

        await interaction.followup.send(embed=embed, ephemeral=True)

        # Log de estadísticas
        from bot.database import log_stat_command
        await log_stat_command(interaction.guild_id, "plan")

    # ── /stats ────────────────────────────────────────────────────────────────

    @app_commands.command(
        name="stats",
        description="Ver estadísticas de publicaciones y comandos usados.",
    )
    async def stats(self, interaction: discord.Interaction) -> None:
        """Muestra estadísticas del servidor en los últimos 7 días."""
        await interaction.response.defer(ephemeral=True)

        # Obtener estadísticas
        stats_posts = await get_stats_posts(interaction.guild_id, days=7)
        stats_commands = await get_stats_commands(interaction.guild_id, days=7)

        embed = discord.Embed(
            title="📈 Estadísticas (últimos 7 días)",
            color=SUCCESS_COLOR,
        )

        # Publicaciones por tipo
        if stats_posts:
            posts_text = ""
            total_posts = sum(stats_posts.values())
            for content_type, count in sorted(stats_posts.items(), key=lambda x: x[1], reverse=True):
                posts_text += f"• {content_type.capitalize()}: {count}\n"
            embed.add_field(
                name=f"📸 Publicaciones ({total_posts} total)",
                value=posts_text,
                inline=False,
            )
        else:
            embed.add_field(
                name="📸 Publicaciones",
                value="Sin publicaciones en los últimos 7 días.",
                inline=False,
            )

        # Comandos más usados
        if stats_commands:
            commands_text = ""
            total_commands = sum(stats_commands.values())
            for cmd, count in sorted(stats_commands.items(), key=lambda x: x[1], reverse=True)[:5]:
                commands_text += f"• `/{cmd}`: {count}\n"
            embed.add_field(
                name=f"⚡ Comandos más usados ({total_commands} total)",
                value=commands_text,
                inline=False,
            )
        else:
            embed.add_field(
                name="⚡ Comandos",
                value="Sin comandos usados en los últimos 7 días.",
                inline=False,
            )

        embed.set_footer(text="Las estadísticas se actualizan en tiempo real.")

        await interaction.followup.send(embed=embed, ephemeral=True)

        # Log de estadísticas
        from bot.database import log_stat_command
        await log_stat_command(interaction.guild_id, "stats")

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
    await bot.add_cog(UtilidadCog(bot))
