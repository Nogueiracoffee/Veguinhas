import discord
from discord.ext import commands
import random
import json
import os

TOKEN = "MTMzMDM4NTEzNTkzMzMyNTM3Mw.Gx9HJU.2cuRPgW7ZYRjLqgk9-1iEfftdvzXgsQhof-2RE"
# Configurações básicas
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Caminho do arquivo JSON
DB_FILE = "vegas_data.json"

# Lista de símbolos do caça-níquel
bet_symbols = ["🐸", "🐵", "🐰", "🦊", "🐻", "🐼"]

# Carrega ou cria o banco de dados
def load_database():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({}, f)
    with open(DB_FILE, "r") as f:
        return json.load(f)

# Salva o banco de dados
def save_database(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Comando de jogo
@bot.command()
async def vegas(ctx):
    user_id = str(ctx.author.id)
    user_name = ctx.author.name

    # Carrega o banco de dados
    data = load_database()

    # Se o usuário não estiver no banco, cria com 0 saldo
    if user_id not in data:
        data[user_id] = {
            "nome": user_name,
            "escolte": 0
        }
        save_database(data)
        await ctx.send(f"👋 | {ctx.author.mention}, você foi registrado com **0 escoltes**. Assim que tiver escoltes, poderá jogar usando este comando!")
        return

    # Consulta o saldo
    saldo = data[user_id]["escolte"]

    # Verifica se tem saldo suficiente
    if saldo < 3:
        await ctx.send(f"❌ | {ctx.author.mention}, você precisa de pelo menos **3 escoltes** para jogar. Seu saldo atual: `{saldo}`.")
        return

    # Cobra 3 créditos para girar
    data[user_id]["escolte"] -= 3

    # Gira os slots
    slot1 = random.choice(bet_symbols)
    slot2 = random.choice(bet_symbols)
    slot3 = random.choice(bet_symbols)

    resultado = f"""
🎰 | {ctx.author.mention}, você girou a roleta:

┌──────────────┐
│ {slot1} │ {slot2} │ {slot3} │
└──────────────┘
"""

    # Calcula o resultado
    if slot1 == slot2 == slot3:
        ganho = 20
        data[user_id]["escolte"] += ganho
        resultado += f"\n💰 | Trinca! Você ganhou **{ganho} escoltes**!"
    elif slot1 == slot2 or slot2 == slot3 or slot1 == slot3:
        ganho = 15
        data[user_id]["escolte"] += ganho
        resultado += f"\n✨ | Par! Você ganhou **{ganho} escoltes**!"
    else:
        resultado += "\n😢 | Nenhuma combinação. Melhor sorte na próxima!"

    # Mostra saldo final
    resultado += f"\n💼 | Saldo atual: `{data[user_id]['escolte']}` escoltes."

    # Salva o banco
    save_database(data)

    # Envia o resultado
    await ctx.send(resultado)

# Inicia o bot
bot.run('MTMzMDM4NTEzNTkzMzMyNTM3Mw.Gx9HJU.2cuRPgW7ZYRjLqgk9-1iEfftdvzXgsQhof-2RE')

