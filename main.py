import os
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    print(f"Bot iniciado! Conectado como {bot.user}")

@bot.command()
async def falar(ctx, *, mensagem):
    # Apaga a mensagem original
    await ctx.message.delete()

    # Bot envia a mensagem
    await ctx.send(mensagem)

bot.run(TOKEN)
