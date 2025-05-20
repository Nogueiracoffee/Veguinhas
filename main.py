import discord
from discord.ext import commands
import random
import json
import os
import asyncio

# CONFIGURAÇÃO DO BOT
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# ARQUIVO DE BANCO DE DADOS
DB_FILE = "vegas_data.json"

# EMOJIS E PESOS
EMOJIS = ["🍒", "⏳", "☕", "🍀", "💎", "♾️"]
PESOS = [40, 25, 15, 10, 7, 3]  # Frequência
VALORES = {
    "🍒": 1,
    "⏳": 2,
    "☕": 3,
    "🍀": 5,
    "💎": 7,
    "♾️": 10
}

# DB

def load_database():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({}, f)
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_database(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# FUNÇÕES

def gerar_matriz():
    return [[random.choices(EMOJIS, PESOS)[0] for _ in range(4)] for _ in range(4)]

def contar_emojis(matriz):
    contagem = {}
    for linha in matriz:
        for emoji in linha:
            contagem[emoji] = contagem.get(emoji, 0) + 1
    return contagem

def quebrar_e_drop(matriz):
    ganhos = 0
    alterado = True

    while alterado:
        contagem = contar_emojis(matriz)
        quebrar = [emoji for emoji, count in contagem.items() if count >= 4]
        if not quebrar:
            alterado = False
            break

        # Remove os emojis a serem quebrados e soma ganhos
        for i in range(4):
            for j in range(4):
                if matriz[i][j] in quebrar:
                    ganhos += VALORES[matriz[i][j]]
                    matriz[i][j] = None

        # Drop
        for col in range(4):
            nova_coluna = [matriz[linha][col] for linha in range(4) if matriz[linha][col] is not None]
            faltam = 4 - len(nova_coluna)
            novos = [random.choices(EMOJIS, PESOS)[0] for _ in range(faltam)]
            nova_coluna = novos + nova_coluna
            for linha in range(4):
                matriz[linha][col] = nova_coluna[linha]

    return matriz, ganhos

# COMANDO

@bot.command()
async def vegas(ctx):
    user_id = str(ctx.author.id)
    user_name = ctx.author.name
    data = load_database()

    if user_id not in data:
        data[user_id] = {"nome": user_name, "escolte": 0}
        save_database(data)
        await ctx.send(f"👋 | {ctx.author.mention}, registrado com 0 escoltes. Peça para um admin adicionar saldo!")
        return

    saldo = data[user_id]["escolte"]
    if saldo < 2:
        await ctx.send(f"❌ | {ctx.author.mention}, você precisa de pelo menos 3 escoltes. Saldo: `{saldo}`")
        return

    data[user_id]["escolte"] -= 3
    save_database(data)

    mensagem = await ctx.send(f"🎰 | {ctx.author.mention} puxou a alavanca...")

    matriz = gerar_matriz()
    for _ in range(6):
        animacao = gerar_matriz()
        vis = "\n".join([" ".join(linha) for linha in animacao])
        await mensagem.edit(content=f"🎰 | {ctx.author.mention} girando...
```
{vis}
```")
        await asyncio.sleep(0.3)

    matriz, ganho_total = quebrar_e_drop(matriz)
    vis_final = "\n".join([" ".join(linha) for linha in matriz])

    data[user_id]["escolte"] += ganho_total
    save_database(data)

    resultado = f"🎰 | {ctx.author.mention} terminou o giro:
```
{vis_final}
```
"
    if ganho_total > 0:
        resultado += f"💸 Você ganhou **{ganho_total} escoltes**!
"
    else:
        resultado += "😢 Nenhuma combinação suficiente para ganhar.
"

    resultado += f"💼 | Saldo atual: `{data[user_id]['escolte']}` escoltes."
    await mensagem.edit(content=resultado)

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
