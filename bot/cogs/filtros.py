"""
filtros.py – InstaShift
=======================
Comandos de slash para gestionar filtros en feeds de Instagram.

Comandos disponibles
--------------------
/filtro add    – Agregar un nuevo filtro a un feed
/filtro list   – Listar todos los filtros de un feed
/filtro remove – Eliminar un filtro
"""

from __future__ import annotations

import logging
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from bot.database import add_filter, remove_filter, get_filters, get_feeds

# ── Logger del módulo ─────────────────────────────────────────────────────────
log = logging.getLogger(__name__)

# ── Paleta de colores para embeds ─────────────────────────────────────────────
FILTER_COLOR = 0x5865F2
SUCCESS_COLOR = 0x00B06B
ERROR_COLOR = 0xFF4444
INFO_COLOR = 0x5865F2


# ══════════════════════════════════════════════════════════════════════════════
# Cog de gestión de filtros
# ══════════════════════════════════════════════════════════════════════════════

class FiltrosCog(commands.Cog, name="Filtros"):
    """Comandos slash para gestionar filtros en feeds."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # ── Grupo de comandos /filtro ──────────────────────────────────────────────

    filtro_group = app_commands.Group(
        name="filtro",
        description="Comandos para gestionar filtros en feeds de Instagram"
    )

    # ── /filtro add ────────────────────────────────────────────────────────────

    @filtro_group.command(
        name="add",
        description="Agregar un nuevo filtro a un feed",
    )
    @app_commands.describe(
        feed_id="ID del feed al que agregar el filtro",
        tipo="Tipo de filtro: hashtag, mención, o palabra clave",
        valor="El hashtag, mención o palabra a filtrar",
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def filtro_add(
        self,
        interaction: discord.Interaction,
        feed_id: int,
        tipo: str,
        valor: str,
    ) -> None:
        """Agrega un nuevo filtro a un feed."""
        await interaction.response.defer(ephemeral=True)

        # Validar que el feed existe
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

        # Validar tipo de filtro
        tipos_validos = ["hashtag", "mención", "palabra"]
        if tipo.lower() not in tipos_validos:
            embed = discord.Embed(
                title="❌ Tipo de filtro inválido",
                description=f"Tipos válidos: {', '.join(tipos_validos)}",
                color=ERROR_COLOR,
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # Agregar filtro a la base de datos
        filter_id = await add_filter(
            feed_id=feed_id,
            filter_type=tipo.lower(),
            filter_value=valor,
        )

        if filter_id:
            embed = discord.Embed(
                title="✅ Filtro agregado",
                description=(
                    f"Filtro de **{tipo}** agregado al feed **@{feed['ig_account']**.\n"
                    f"Tipo: `{tipo}`\n"
                    f"Valor: `{valor}`\n"
                    f"Filtro ID: `#{filter_id}`"
                ),
                color=SUCCESS_COLOR,
            )
        else:
            embed = discord.Embed(
                title="❌ Error al agregar filtro",
                description="Ocurrió un error al agregar el filtro.",
                color=ERROR_COLOR,
            )

        await interaction.followup.send(embed=embed, ephemeral=True)

        # Log de estadísticas
        from bot.database import log_stat_command
        await log_stat_command(interaction.guild_id, "filtro add")

    # ── /filtro list ───────────────────────────────────────────────────────────

    @filtro_group.command(
        name="list",
        description="Listar todos los filtros de un feed",
    )
    @app_commands.describe(
        feed_id="ID del feed del que listar los filtros",
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def filtro_list(
        self,
        interaction: discord.Interaction,
        feed_id: int,
    ) -> None:
        """Lista todos los filtros de un feed."""
        await interaction.response.defer(ephemeral=True)

        # Validar que el feed existe
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

        # Obtener filtros del feed
        filtros = await get_filters(feed_id)

        if not filtros:
            await interaction.followup.send(
                f"📭 El feed **@{feed['ig_account']}** no tiene filtros.",
                ephemeral=True,
            )
            return

        # Formatear lista de filtros
        lineas = []
        for f in filtros:
            lineas.append(
                f"**#{f['id']}** - **{f['filter_type']}**: `{f['filter_value']}`"
            )

        embed = discord.Embed(
            title="🔍 Filtros activos",
            description="\n".join(lineas),
            color=FILTER_COLOR,
        )
        embed.set_footer(text="Usa /filtro remove <id> para eliminar un filtro.")

        await interaction.followup.send(embed=embed, ephemeral=True)

        # Log de estadísticas
        from bot.database import log_stat_command
        await log_stat_command(interaction.guild_id, "filtro list")

    # ── /filtro remove ─────────────────────────────────────────────────────────

    @filtro_group.command(
        name="remove",
        description="Eliminar un filtro",
    )
    @app_commands.describe(
        filter_id="ID del filtro a eliminar",
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def filtro_remove(
        self,
        interaction: discord.Interaction,
        filter_id: int,
    ) -> None:
        """Elimina un filtro."""
        await interaction.response.defer(ephemeral=True)

        # Eliminar filtro
        eliminado = await remove_filter(filter_id)

        if eliminado:
            embed = discord.Embed(
                title="🗑️ Filtro eliminado",
                description=f"El filtro **#{filter_id}** ha sido eliminado.",
                color=SUCCESS_COLOR,
            )
        else:
            embed = discord.Embed(
                title="❌ Filtro no encontrado",
                description=f"No existe un filtro con ID **{filter_id}**.",
                color=ERROR_COLOR,
            )

        await interaction.followup.send(embed=embed, ephemeral=True)

        # Log de estadísticas
        from bot.database import log_stat_command
        await log_stat_command(interaction.guild_id, "filtro remove")

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
    cog = FiltrosCog(bot)
    bot.tree.add_command(cog.filtro_group)
    await bot.add_cog(cog)
