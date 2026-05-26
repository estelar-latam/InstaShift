"""
filtros.py – InstaShift
=======================
Comandos de slash para gestionar filtros de feeds.

Comandos disponibles
--------------------
/filtro add    – Agregar filtro a un feed (hashtag, mención, keyword)
/filtro remove – Eliminar un filtro por su ID
/filtro list   – Listar todos los filtros de un feed
"""

from __future__ import annotations

import logging
from typing import Literal, Optional

import discord
from discord import app_commands
from discord.ext import commands

from bot.database import add_filter, get_filters, remove_filter

# ── Logger del módulo ─────────────────────────────────────────────────────────
log = logging.getLogger(__name__)

# ── Paleta de colores para embeds ─────────────────────────────────────────────
FILTRO_COLOR = 0x00B06B  # Verde
SUCCESS_COLOR = 0x00B06B
ERROR_COLOR = 0xFF4444
INFO_COLOR = 0x5865F2


class FiltrosCog(commands.Cog, name="Filtros"):
    """Comandos slash para gestionar filtros de feeds."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # ── Grupo de comandos /filtro ──────────────────────────────────────────────

    filtro_group = app_commands.Group(
        name="filtro",
        description="Comandos para gestionar filtros de contenido en feeds"
    )

    # ── /filtro add ────────────────────────────────────────────────────────────

    @filtro_group.command(
        name="add",
        description="Agregar un filtro (hashtag, mención o palabra clave) a un feed.",
    )
    @app_commands.describe(
        feed_id="ID del feed al que agregar el filtro",
        tipo="Tipo de filtro: hashtag, mención o keyword",
        valor="El valor del filtro (sin # o @ para hashtag/mención)",
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def filtro_add(
        self,
        interaction: discord.Interaction,
        feed_id: int,
        tipo: Literal["hashtag", "mención", "keyword"],
        valor: str,
    ) -> None:
        """Agrega un filtro a un feed."""
        await interaction.response.defer(ephemeral=True)

        valor = valor.strip()
        if not valor:
            await interaction.followup.send(
                "❌ El valor del filtro no puede estar vacío.", ephemeral=True
            )
            return

        # Convertir tipos en español a inglés
        tipo_db = "mention" if tipo == "mención" else tipo

        # Agregar filtro
        filtro_id = await add_filter(feed_id, tipo_db, valor)

        if filtro_id:
            embed = discord.Embed(
                title="✅ Filtro agregado",
                description=(
                    f"Filtro **{tipo}** ({valor}) agregado al feed **#{feed_id}**.\n"
                    "El feed ahora solo publicará contenido que coincida con este filtro."
                ),
                color=SUCCESS_COLOR,
            )
        else:
            embed = discord.Embed(
                title="❌ Error al agregar filtro",
                description=f"No se pudo agregar el filtro. Verifica que el feed **#{feed_id}** existe.",
                color=ERROR_COLOR,
            )

        await interaction.followup.send(embed=embed, ephemeral=True)

        # Log de estadísticas
        from bot.database import log_stat_command
        await log_stat_command(interaction.guild_id, "filtro add")

    # ── /filtro remove ────────────────────────────────────────────────────────

    @filtro_group.command(
        name="remove",
        description="Eliminar un filtro por su ID.",
    )
    @app_commands.describe(
        filtro_id="ID del filtro a eliminar (obtén la lista con /filtro list)",
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def filtro_remove(
        self,
        interaction: discord.Interaction,
        filtro_id: int,
    ) -> None:
        """Elimina un filtro."""
        await interaction.response.defer(ephemeral=True)

        eliminado = await remove_filter(filtro_id)

        if eliminado:
            embed = discord.Embed(
                title="🗑️ Filtro eliminado",
                description=f"El filtro **#{filtro_id}** ha sido eliminado.",
                color=ERROR_COLOR,
            )
        else:
            embed = discord.Embed(
                title="⚠️ Filtro no encontrado",
                description=f"No existe un filtro con ID **{filtro_id}**.",
                color=INFO_COLOR,
            )

        await interaction.followup.send(embed=embed, ephemeral=True)

        # Log de estadísticas
        from bot.database import log_stat_command
        await log_stat_command(interaction.guild_id, "filtro remove")

    # ── /filtro list ──────────────────────────────────────────────────────────

    @filtro_group.command(
        name="list",
        description="Listar todos los filtros de un feed.",
    )
    @app_commands.describe(
        feed_id="ID del feed cuyo filtros quieres ver",
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def filtro_list(
        self,
        interaction: discord.Interaction,
        feed_id: int,
    ) -> None:
        """Lista todos los filtros activos de un feed."""
        await interaction.response.defer(ephemeral=True)

        filtros = await get_filters(feed_id)

        if not filtros:
            await interaction.followup.send(
                f"📭 El feed **#{feed_id}** no tiene filtros activos.",
                ephemeral=True,
            )
            return

        # Formatear lista de filtros
        lineas = []
        for f in filtros:
            tipo_display = "Mención" if f['filter_type'] == 'mention' else f['filter_type'].capitalize()
            lineas.append(f"**#{f['id']}** [{tipo_display}] `{f['filter_value']}`")

        embed = discord.Embed(
            title=f"🔍 Filtros del feed #{feed_id}",
            description="\n".join(lineas),
            color=FILTRO_COLOR,
        )
        embed.set_footer(text="Usa /filtro remove <id> para eliminar un filtro.")

        await interaction.followup.send(embed=embed, ephemeral=True)

        # Log de estadísticas
        from bot.database import log_stat_command
        await log_stat_command(interaction.guild_id, "filtro list")

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
    await bot.add_cog(FiltrosCog(bot))
