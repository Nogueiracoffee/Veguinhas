import discord
from discord.ext import commands
import random
import json
import os

TOKEN = "MTMzMDM4NTEzNTkzMzMyNTM3Mw.Gx9HJU.2cuRPgW7ZYRjLqgk9-1iEfftdvzXgsQhof-2RE"  # Substitua pelo seu token real

# Define as permissões (intents) que o bot precisa para funcionar corretamente
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# Criar o bot com prefixo
bot = commands.Bot(command_prefix='!', intents=intents)

# Nome do arquivo que será usado como banco de dados para salvar os saldos dos jogadores
DB_FILE = "escolte_banco.json"

# Lista com os símbolos usados no caça-níquel
bet_symbols = ["🐸", "🐵", "🐰", "🦊", "🐻", "🐼"]

# Define o valor mínimo de escoltes para rodar a máquina
minimum_escolte = 3

# Função para carregar os dados do banco de dados (arquivo JSON)
def carregar_dados():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}  # Se o arquivo não existir, retorna um dicionário vazio

# Função para salvar os dados no arquivo JSON
def salvar_dados(dados):
    with open(DB_FILE, "w") as f:
        json.dump(dados, f, indent=4)

# Comando para registrar um jogador na Vegas Machine
@bot.command()
async def vegas(ctx):
    user = ctx.author
    dados = carregar_dados()

    if str(user.id) not in dados:
        # Registra o usuário com 0 escoltes
        dados[str(user.id)] = {
            "nome": user.display_name,
            "escolte": 0
        }
        salvar_dados(dados)
        await ctx.send(
            f"🎰 {user.mention}, você foi registrado na **Vegas Machine**.\n"
            f"Você ainda não tem escoltes. Aguarde um administrador adicionar escoltes para começar a jogar."
        )
    else:
        await ctx.send(f"{user.mention}, você já está registrado. Use `!apostar` quando tiver escoltes.")

# Comando para consultar o saldo atual
@bot.command()
async def saldo(ctx):
    user = ctx.author
    dados = carregar_dados()

    if str(user.id) not in dados:
        await ctx.send(f"{user.mention}, registre-se primeiro com `!vegas`.")
    else:
        escolte = dados[str(user.id)]["escolte"]
        await ctx.send(f"💰 {user.mention}, você tem **{escolte} escoltes**.")

# Comando para mostrar as instruções do jogo
@bot.command()
async def instrucoes(ctx):
    await ctx.send(
        "**Instruções do Jogo:**\n"
        "🎯 3 símbolos iguais = +20 escoltes\n"
        "🎯 2 símbolos iguais = +10 escoltes\n"
        "❌ Nenhum igual = perde os 3 escoltes da rodada\n"
        "🎲 Custo por rodada: 3 escoltes\n"
        "Use `!apostar` para jogar!"
    )

# Comando principal para jogar na máquina
@bot.command()
async def apostar(ctx):
    user = ctx.author
    dados = carregar_dados()

    # Verifica se o jogador está registrado
    if str(user.id) not in dados:
        await ctx.send(f"{user.mention}, registre-se primeiro com `!vegas`.")
        return

    saldo = dados[str(user.id)]["escolte"]
# Verifica se tem escoltes suficientes para apostar
    if saldo < minimum_escolte:
        await ctx.send(f"❌ {user.mention}, você não tem escoltes suficientes para jogar. (Mínimo: {minimum_escolte})")
        return

    # Desconta o valor da aposta
    dados[str(user.id)]["escolte"] -= minimum_escolte

    # Sorteia três símbolos aleatórios
    s1 = random.choice(bet_symbols)
    s2 = random.choice(bet_symbols)
    s3 = random.choice(bet_symbols)

    resultado = f"| {s1} | {s2} | {s3} |"
    ganho = 0  # Inicia com zero de ganho

    # Verifica as combinações para calcular o ganho
    if s1 == s2 == s3:
        ganho = 20
    elif s1 == s2 or s2 == s3 or s1 == s3:
        ganho = 10

    # Adiciona o ganho ao saldo do jogador
    dados[str(user.id)]["escolte"] += ganho
    salvar_dados(dados)

    novo_saldo = dados[str(user.id)]["escolte"]

    # Cria a mensagem de resultado
    msg = f"{user.mention} 🎰 Resultado: `{resultado}`\n"
    if ganho == 20:
        msg += "🏆 **Jackpot!** Você ganhou **20 escoltes!**\n"
    elif ganho == 10:
        msg += "✨ Você ganhou **10 escoltes!**\n"
    else:
        msg += "💀 Você perdeu essa rodada.\n"

    msg += f"💰 Saldo atual: **{novo_saldo} escoltes**"

    # Envia a mensagem no Discord
    await ctx.send(msg)


# Comando para o bot repetir uma mensagem (somente admin)
@bot.command()
@commands.has_permissions(administrator=True)
async def falar(ctx, *, mensagem):
    await ctx.message.delete()
    await ctx.send(mensagem)


# Rodar o bot
bot.run(TOKEN)
