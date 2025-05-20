import discord
from discord.ext import commands
import random
import json
import os

# CONFIGURAÇÃO DO BOT
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# ARQUIVO DE BANCO DE DADOS
DB_FILE = "vegas_data.json"

# SÍMBOLOS DO SLOT
bet_symbols = ["🐸", "🐵", "🐰", "🦊", "🐻", "🐼"]

# FUNÇÃO: CARREGAR BANCO DE DADOS
def load_database():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({}, f)
    with open(DB_FILE, "r") as f:
        return json.load(f)

# FUNÇÃO: SALVAR BANCO DE DADOS
def save_database(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# COMANDO: SLOT !vegas
@bot.command()
async def vegas(ctx):
    user_id = str(ctx.author.id)
    user_name = ctx.author.name
    data = load_database()

    # REGISTRA USUÁRIO NOVO COM 0 ESCOLTES
    if user_id not in data:
        data[user_id] = {
            "nome": user_name,
            "escolte": 0
        }
        save_database(data)
        await ctx.send(f"👋 | {ctx.author.mention}, você foi registrado com **0 escoltes**. Peça para um admin adicionar saldo antes de jogar!")
        return

    # VERIFICA SALDO
    saldo = data[user_id]["escolte"]
    if saldo < 3:
        await ctx.send(f"❌ | {ctx.author.mention}, você precisa de pelo menos **3 escoltes** para jogar. Seu saldo atual: `{saldo}`.")
        return

    # COBRA 3 ESCOLTES
    data[user_id]["escolte"] -= 3

    # GIRA SLOT
    slot1 = random.choice(bet_symbols)
    slot2 = random.choice(bet_symbols)
    slot3 = random.choice(bet_symbols)

    resultado = f"""
🎰 | {ctx.author.mention}, você girou a roleta:

┌──────────────┐
│ {slot1} │ {slot2} │ {slot3} │
└──────────────┘
"""

    # CALCULA GANHOS
    if slot1 == slot2 == slot3:
        ganho = 10
        data[user_id]["escolte"] += ganho
        resultado += f"\n💰 | Trinca! Você ganhou **{ganho} escoltes**!"
    elif slot1 == slot2 or slot2 == slot3 or slot1 == slot3:
        ganho = 5
        data[user_id]["escolte"] += ganho
        resultado += f"\n✨ | Par! Você ganhou **{ganho} escoltes**!"
    else:
        resultado += "\n😢 | Nenhuma combinação. Melhor sorte na próxima!"

    # MOSTRA SALDO FINAL
    resultado += f"\n💼 | Saldo atual: `{data[user_id]['escolte']}` escoltes."

    # SALVA DADOS
    save_database(data)
    await ctx.send(resultado)

# COMANDO ADMIN: ADICIONAR ESCOLTE
@bot.command()
@commands.has_permissions(administrator=True)
async def addescolte(ctx, member: discord.Member, valor: int):
    data = load_database()
    user_id = str(member.id)
    user_name = member.name

    # REGISTRA USUÁRIO CASO NÃO EXISTA
    if user_id not in data:
        data[user_id] = {
            "nome": user_name,
            "escolte": 0
        }

    data[user_id]["escolte"] += valor
    save_database(data)
    await ctx.send(f"✅ | Adicionado **{valor} escoltes** para {member.mention}. Saldo atual: `{data[user_id]['escolte']}`.")

# ERRO DE PERMISSÃO NO COMANDO ADMIN
@addescolte.error
async def addescolte_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ | Você não tem permissão para usar este comando.")

# INICIAR BOT
bot.run('MTMzMDM4NTEzNTkzMzMyNTM3Mw.Gx9HJU.2cuRPgW7ZYRjLqgk9-1iEfftdvzXgsQhof-2RE')


