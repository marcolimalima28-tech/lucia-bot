import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────
#  CONFIGURACIÓN  (edita a tu gusto)
# ─────────────────────────────────────────
CANAL_BIENVENIDA  = "bienvenida"          # nombre del canal de bienvenida
CANAL_GUIA        = "guía-del-servidor"   # nombre del canal de la guía
ROL_NUEVO_MIEMBRO = "Nuevo Miembro"       # rol que se asigna automáticamente (opcional)

GUIA_TITULO = "📖  Guía del Servidor"

GUIA_CONTENIDO = """
╔══════════════════════════════════════════╗
║        ¡BIENVENIDO AL SERVIDOR!          ║
╚══════════════════════════════════════════╝

👋  Gracias por unirte. Aquí tienes todo lo que necesitas saber:

──────────────────────────────────────────
📌  REGLAS DEL SERVIDOR
──────────────────────────────────────────
1️⃣  Respeta a todos los miembros en todo momento.
2️⃣  No spam, publicidad no autorizada ni flood.
3️⃣  Usa cada canal para su propósito correcto.
4️⃣  Contenido NSFW queda totalmente prohibido.
5️⃣  Sigue las normas de Discord: https://discord.com/terms

──────────────────────────────────────────
📂  CANALES PRINCIPALES
──────────────────────────────────────────
👋  #bienvenida       → Recibimos a los nuevos miembros
📖  #guía-del-servidor → Estás aquí — toda la info del servidor
💬  #general          → Chat libre para todos
❓  #ayuda            → Pregunta lo que necesites
🎮  #off-topic        → Memes, juegos y charla casual

──────────────────────────────────────────
🤖  COMANDOS DEL BOT
──────────────────────────────────────────
!guia     → Muestra esta guía en cualquier canal
!reglas   → Muestra las reglas del servidor
!info     → Información del servidor

──────────────────────────────────────────
🌟  CÓMO PARTICIPAR
──────────────────────────────────────────
✅  Preséntate en #general
✅  Lee las reglas y respétalas
✅  ¡Diviértete y comparte con la comunidad!

──────────────────────────────────────────
📬  CONTACTO
──────────────────────────────────────────
¿Tienes algún problema? Menciona a @Moderadores
o envía un mensaje directo a los administradores.

¡Esperamos que disfrutes tu estancia! 🎉
"""

REGLAS_CONTENIDO = """
📋  **REGLAS DEL SERVIDOR**

**1.** Respeta a todos los miembros.
**2.** No spam ni autopromoción sin permiso.
**3.** Usa los canales correctamente.
**4.** Prohibido el contenido NSFW.
**5.** Cumple los [Términos de Servicio de Discord](https://discord.com/terms).

El incumplimiento puede resultar en advertencia, silencio o ban.
"""

# ─────────────────────────────────────────
#  INICIALIZACIÓN DEL BOT
# ─────────────────────────────────────────
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


# ─────────────────────────────────────────
#  EVENTOS
# ─────────────────────────────────────────
@bot.event
async def on_ready():
    print(f"✅  Bot conectado como {bot.user} (ID: {bot.user.id})")
    print("─────────────────────────────────────")

    # Publicar guía en todos los servidores donde está el bot
    for guild in bot.guilds:
        await publicar_guia_servidor(guild)

    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="el servidor 👀"
        )
    )


@bot.event
async def on_member_join(member: discord.Member):
    """Envía mensaje de bienvenida cuando entra un nuevo miembro."""
    guild = member.guild

    # Buscar canal de bienvenida
    canal = discord.utils.get(guild.text_channels, name=CANAL_BIENVENIDA)
    if canal is None:
        canal = await crear_canal_si_no_existe(guild, CANAL_BIENVENIDA,
                                               "Canal de bienvenida para nuevos miembros")

    if canal:
        embed = discord.Embed(
            title=f"👋  ¡Bienvenido/a, {member.display_name}!",
            description=(
                f"Hola {member.mention}, ¡nos alegra tenerte aquí! 🎉\n\n"
                f"📖  Echa un vistazo a <#{discord.utils.get(guild.text_channels, name=CANAL_GUIA).id if discord.utils.get(guild.text_channels, name=CANAL_GUIA) else canal.id}> "
                f"para conocer las reglas y canales del servidor.\n\n"
                f"💬  Preséntate en **#general** cuando quieras.\n"
                f"❓  Si necesitas ayuda, estamos en **#ayuda**.\n\n"
                f"¡Disfruta tu estancia! 🌟"
            ),
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Miembro #{guild.member_count} del servidor")
        await canal.send(embed=embed)

    # Asignar rol de nuevo miembro si existe
    rol = discord.utils.get(guild.roles, name=ROL_NUEVO_MIEMBRO)
    if rol:
        try:
            await member.add_roles(rol)
        except discord.Forbidden:
            print(f"⚠️  Sin permisos para asignar rol a {member.display_name}")


# ─────────────────────────────────────────
#  COMANDOS
# ─────────────────────────────────────────
@bot.command(name="guia")
async def cmd_guia(ctx):
    """!guia — Muestra la guía del servidor."""
    embed = discord.Embed(
        title=GUIA_TITULO,
        description=GUIA_CONTENIDO,
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"Servidor: {ctx.guild.name}")
    await ctx.send(embed=embed)


@bot.command(name="reglas")
async def cmd_reglas(ctx):
    """!reglas — Muestra las reglas del servidor."""
    embed = discord.Embed(
        title="📋  Reglas del Servidor",
        description=REGLAS_CONTENIDO,
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)


@bot.command(name="info")
async def cmd_info(ctx):
    """!info — Muestra información del servidor."""
    guild = ctx.guild
    embed = discord.Embed(
        title=f"ℹ️  {guild.name}",
        color=discord.Color.gold()
    )
    embed.add_field(name="👥  Miembros", value=guild.member_count, inline=True)
    embed.add_field(name="📅  Creado el", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="👑  Dueño", value=str(guild.owner), inline=True)
    embed.add_field(name="📂  Canales", value=len(guild.text_channels), inline=True)
    embed.add_field(name="🔊  Canales de voz", value=len(guild.voice_channels), inline=True)
    embed.add_field(name="🎭  Roles", value=len(guild.roles), inline=True)
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    await ctx.send(embed=embed)


@bot.command(name="publicar_guia")
@commands.has_permissions(administrator=True)
async def cmd_publicar_guia(ctx):
    """!publicar_guia — (Solo admins) Publica/actualiza la guía en el canal oficial."""
    await publicar_guia_servidor(ctx.guild)
    await ctx.send("✅  Guía publicada correctamente.", delete_after=5)


# ─────────────────────────────────────────
#  FUNCIONES AUXILIARES
# ─────────────────────────────────────────
async def crear_canal_si_no_existe(guild: discord.Guild, nombre: str, topic: str = ""):
    """Crea un canal de texto si no existe y devuelve el canal."""
    canal = discord.utils.get(guild.text_channels, name=nombre)
    if canal is None:
        try:
            canal = await guild.create_text_channel(nombre, topic=topic)
            print(f"📌  Canal #{nombre} creado en {guild.name}")
        except discord.Forbidden:
            print(f"⚠️  Sin permisos para crear #{nombre} en {guild.name}")
            return None
    return canal


async def publicar_guia_servidor(guild: discord.Guild):
    """Publica (o actualiza) la guía en el canal designado."""
    canal = discord.utils.get(guild.text_channels, name=CANAL_GUIA)
    if canal is None:
        canal = await crear_canal_si_no_existe(guild, CANAL_GUIA,
                                               "Guía oficial del servidor")
    if canal is None:
        return

    embed = discord.Embed(
        title=GUIA_TITULO,
        description=GUIA_CONTENIDO,
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"Servidor: {guild.name}  •  Actualizado automáticamente")

    # Buscar si ya existe un mensaje de la guía y editarlo
    async for msg in canal.history(limit=20):
        if msg.author == bot.user and msg.embeds:
            await msg.edit(embed=embed)
            print(f"♻️   Guía actualizada en #{canal.name} ({guild.name})")
            return

    # Si no existe, publicarlo nuevo
    await canal.send(embed=embed)
    print(f"📖  Guía publicada en #{canal.name} ({guild.name})")


# ─────────────────────────────────────────
#  ARRANQUE
# ─────────────────────────────────────────
if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌  Error: No se encontró DISCORD_TOKEN en el archivo .env")
        print("   Crea un archivo .env con: DISCORD_TOKEN=tu_token_aquí")
    else:
        bot.run(token)
