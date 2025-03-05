import discord
from discord.ext import commands
import os
import json
import random

TOKEN = "MTMzMDM4NTEzNTkzMzMyNTM3Mw.Gx9HJU.2cuRPgW7ZYRjLqgk9-1iEfftdvzXgsQhof-2RE"  # Substitua pelo seu token real

# Configurar intents
intents = discord.Intents.default()
intents.message_content = True

# Criar o bot com prefixo
bot = commands.Bot(command_prefix='!', intents=intents)

# Armazenamento de cafés e saldo
cafes_por_usuario = {}
saldo_usuarios = {}
tickets_usuarios = {}
ARQUIVO_SALDO = "saldo_usuarios.txt"


# Funções para carregar e salvar saldos
def carregar_saldo():
    global saldo_usuarios

    if os.path.exists(ARQUIVO_SALDO):
        try:
            with open(ARQUIVO_SALDO, "r", encoding="utf-8") as f:
                data = json.load(f)
                saldo_usuarios = data.get('saldos', {})
        except (json.JSONDecodeError, FileNotFoundError):
            print("Erro ao carregar o arquivo de saldo. Criando novo arquivo.")
            saldo_usuarios = {}
            salvar_saldo()

def salvar_saldo():
    with open(ARQUIVO_SALDO, "w", encoding="utf-8") as f:
        json.dump({'saldos': saldo_usuarios}, f, indent=4)


# Evento quando o bot estiver pronto
@bot.event
async def on_ready():
    carregar_saldo()
    print(f'Bot conectado como {bot.user}')


    # Comando para exibir inventário
    @bot.command()
    async def perfil(ctx):
        user_id = str(ctx.author.id)
        saldo = saldo_usuarios.get(user_id, 0)
        cargo = ctx.author.top_role.name
        await ctx.send(
    f"📜 **Inventário de {ctx.author.display_name}**\n"
    f"━━━━━━━━━━━━━━━━━━━\n"
    f"🏷️ **Cargo:** {cargo}\n"
    f"🪙 **Escoltes:** {saldo}\n"
    f"━━━━━━━━━━━━━━━━━━━"
)

# Comando de teste
@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')


# Comando para contar cafés
@bot.command()
async def café(ctx):
    user_id = str(ctx.author.id)
    cafes_por_usuario[user_id] = cafes_por_usuario.get(user_id, 0) + 1
    total_cafes = cafes_por_usuario[user_id]
    await ctx.send(f"{ctx.author.mention} já tomou {total_cafes}° ☕")


# Comando para adicionar saldo manualmente (admin)
@bot.command()
@commands.has_permissions(administrator=True)
async def addsaldo(ctx, membro: discord.Member, quantidade: int):
    user_id = str(membro.id)
    saldo_usuarios[user_id] = saldo_usuarios.get(user_id, 0) + quantidade
    salvar_saldo()
    await ctx.send(f"{membro.mention} Recebeu {quantidade} Escoltes! Saldo atual: {saldo_usuarios[user_id]} 🪙")


# Comando para transferir saldo entre usuários
@bot.command()
async def transferir(ctx, membro: discord.Member, quantidade: int):
    sender_id = str(ctx.author.id)
    receiver_id = str(membro.id)

    if sender_id not in saldo_usuarios or saldo_usuarios[sender_id] < quantidade:
        await ctx.send(f"{ctx.author.mention}, Você não tem saldo suficiente para transferir!")
        return

    saldo_usuarios[sender_id] -= quantidade
    saldo_usuarios[receiver_id] = saldo_usuarios.get(receiver_id, 0) + quantidade
    salvar_saldo()

    await ctx.send(f"{ctx.author.mention} Transferiu {quantidade} Escoltes para {membro.mention}! 💰")


# Comando para exibir ranking de saldo
@bot.command()
async def rank(ctx):
    if not saldo_usuarios:
        await ctx.send("Nenhum usuário tem saldo registrado ainda.")
        return

    ranking_lista = sorted(saldo_usuarios.items(), key=lambda x: x[1], reverse=True)
    mensagem = " **Ranking de Escoltes** 🪙\n"

    for i, (user_id, saldo) in enumerate(ranking_lista[:10], start=1):  # Mostra os top 10
        membro = await ctx.guild.fetch_member(int(user_id))
        mensagem += f"**{i}. {membro.display_name}** {saldo}  🪙\n"

    await ctx.send(mensagem)


# Comando para o bot repetir uma mensagem (somente admin)
@bot.command()
@commands.has_permissions(administrator=True)
async def falar(ctx, *, mensagem):
    await ctx.message.delete()
    await ctx.send(mensagem)


# Rodar o bot
bot.run(TOKEN)
