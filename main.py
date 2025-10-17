import discord
from discord.ext import commands

# =========================
# CONFIGURAÇÃO DO BOT
# =========================

# Coloque seu token do bot aqui (token do bot, não do usuário)
TOKEN = "MTMzMDM4NTEzNTkzMzMyNTM3Mw.G2NG39.jgUxrjNIFshlt7OSHj6GI7uM2QxPdnsyijY5ko"

# Configuração de intents
intents = discord.Intents.default()
intents.message_content = True  # Permite ler mensagens para comandos
bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# COMANDOS DO BOT
# =========================

# Comando de administrador: fazer o bot falar
@bot.command()
@commands.has_permissions(administrator=True)
async def falar(ctx, *, mensagem):
    """Faz o bot repetir uma mensagem e apaga o comando original"""
    await ctx.message.delete()
    await ctx.send(mensagem)

# Tratamento de erros do comando
@falar.error
async def falar_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ | Você não tem permissão para usar este comando.")

# =========================
# INICIAR BOT
# =========================

if __name__ == "__main__":
    print("Bot iniciado. Conectando ao Discord...")
    bot.run(TOKEN)
