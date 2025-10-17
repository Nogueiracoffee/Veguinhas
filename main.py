import discord
from discord.ext import commands

# Token do bot (coloque seu token aqui)
TOKEN = "MTMzMDM4NTEzNTkzMzMyNTM3Mw.G2NG39.jgUxrjNIFshlt7OSHj6GI7uM2QxPdnsyijY5ko"

# Configuração do bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Comando de administrador: fazer o bot falar
@bot.command()
@commands.has_permissions(administrator=True)
async def falar(ctx, *, mensagem):
    await ctx.message.delete()
    await ctx.send(mensagem)

# Erro de permissão
@falar.error
async def falar_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ | Você não tem permissão para usar este comando.")

# Rodar o bot
bot.run(TOKEN)
