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

GUIA_TITULO = "⚔️  Guía de Santa Lucía — MU Online Season 21 Part 2-3"
COLOR_ORO  = discord.Color.from_rgb(232, 181, 74)
COLOR_ROJO = discord.Color.from_rgb(163, 18, 28)

GUIA_CONTENIDO = """
🛡️ **¡Bienvenido, guerrero, a Santa Lucía!**
Comunidad oficial de nuestro servidor de MU Online.

**📜 REGLAS**
1️⃣ Respeta a todos los jugadores y al staff.
2️⃣ Prohibido el spam, flood y la publicidad de otros servidores.
3️⃣ Prohibido usar o promover hacks, bots o exploits.
4️⃣ Nada de estafas: el comercio es bajo tu responsabilidad.
5️⃣ Usa cada canal para su propósito.
6️⃣ Prohibido contenido NSFW. Cumple los términos de Discord.

**📌 INFORMACIÓN**
#bienvenida · #reglas · #guía-del-servidor · #anuncios · #actualizaciones · #eventos

**⚔️ COMUNIDAD**
#general · #capturas · #busco-party · #comercio · #guilds · #castle-siege

**🆘 SOPORTE**
#ayuda · #reportar-bugs · #tickets

**🤖 COMANDOS**
`!guia` — Muestra esta guía
`!reglas` — Reglas del servidor
`!info` — Información del Discord

🛡️ *Que la luz de Santa Lucía guíe tu espada.*
"""

REGLAS_CONTENIDO = """
**1.** Respeta a todos los jugadores y al staff.
**2.** Prohibido el spam, flood y la publicidad de otros servidores.
**3.** Prohibido usar o promover hacks, bots o exploits.
**4.** Nada de estafas: el comercio es bajo tu responsabilidad.
**5.** Usa cada canal para su propósito.
**6.** Prohibido contenido NSFW. Cumple los [Términos de Discord](https://discord.com/terms).

El incumplimiento puede resultar en advertencia, silencio o ban.
"""


def buscar_canal(guild, nombre):
    """Encuentra un canal aunque tenga emojis o prefijos (ej: '👋bienvenida')."""
    for c in guild.text_channels:
        if c.name == nombre or nombre in c.name:
            return c
    return None

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
            name="Santa Lucía ⚔️"
        )
    )


@bot.event
async def on_member_join(member: discord.Member):
    """Envía mensaje de bienvenida cuando entra un nuevo miembro."""
    guild = member.guild

    # Buscar canal de bienvenida
    canal = buscar_canal(guild, CANAL_BIENVENIDA)
    if canal is None:
        canal = await crear_canal_si_no_existe(guild, CANAL_BIENVENIDA,
                                               "Canal de bienvenida para nuevos miembros")

    if canal:
        embed = discord.Embed(
            title=f"⚔️  ¡Bienvenido/a a Santa Lucía, {member.display_name}!",
            description=(
                f"Hola {member.mention}, ¡nos alegra tenerte aquí! 🎉\n\n"
                f"📖  Echa un vistazo a <#{buscar_canal(guild, CANAL_GUIA).id if buscar_canal(guild, CANAL_GUIA) else canal.id}> "
                f"para conocer las reglas y canales del servidor.\n\n"
                f"💬  Preséntate en **#general** y busca grupo en **#busco-party**.\n"
                f"❓  Si necesitas ayuda, estamos en **#ayuda**.\n\n"
                f"🛡️ ¡Que la luz de Santa Lucía guíe tu espada!"
            ),
            color=COLOR_ORO
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
        color=COLOR_ORO
    )
    embed.set_footer(text=f"Servidor: {ctx.guild.name}")
    await ctx.send(embed=embed)


@bot.command(name="reglas")
async def cmd_reglas(ctx):
    """!reglas — Muestra las reglas del servidor."""
    embed = discord.Embed(
        title="📋  Reglas del Servidor",
        description=REGLAS_CONTENIDO,
        color=COLOR_ROJO
    )
    await ctx.send(embed=embed)


@bot.command(name="info")
async def cmd_info(ctx):
    """!info — Muestra información del servidor."""
    guild = ctx.guild
    embed = discord.Embed(
        title=f"ℹ️  {guild.name}",
        color=COLOR_ORO
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
    canal = buscar_canal(guild, nombre)
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
    canal = buscar_canal(guild, CANAL_GUIA)
    if canal is None:
        canal = await crear_canal_si_no_existe(guild, CANAL_GUIA,
                                               "Guía oficial del servidor")
    if canal is None:
        return

    embed = discord.Embed(
        title=GUIA_TITULO,
        description=GUIA_CONTENIDO,
        color=COLOR_ORO
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
