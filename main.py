import discord
from discord.ext import commands
import os

# CONFIGURAÇÃO DO BOT
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# COMANDO ADMIN: FAZER O BOT FALAR
@bot.command()
@commands.has_permissions(administrator=True)
async def falar(ctx, *, mensagem):
    await ctx.message.delete()  # Exclui a mensagem do comando
    await ctx.send(mensagem)    # O bot envia a mensagem no lugar

# ERRO DE PERMISSÃO
@falar.error
async def falar_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ | Você não tem permissão para usar este comando.")

# INICIAR BOT
TOKEN = os.getenv('DISCORD_TOKEN')
bot.run("MTMzMDM4NTEzNTkzMzMyNTM3Mw.G_HZOA.8GOZI3IFInYm5-Ep9IRaQAfBty20QrLBgw6hSI")
