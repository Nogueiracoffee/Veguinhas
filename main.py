import os
import discord
from discord.ext import commands
import threading
import http.server
import socketserver

# --- Servidor para manter o app "vivo" no Koyeb ---
def keep_alive():
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", 8000), handler) as httpd:
        print("Servidor keep-alive rodando na porta 8000")
        httpd.serve_forever()

threading.Thread(target=keep_alive, daemon=True).start()
# ---------------------------------------------------

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot iniciado! Conectado como {bot.user}")

@bot.command()
async def falar(ctx, *, mensagem):
    await ctx.message.delete()
    await ctx.send(mensagem)

bot.run(TOKEN)
