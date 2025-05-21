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

# SÍMBOLOS DO SLOT
bet_symbols = ["🍒", "⏳", "⭐", "🍀", "💎", "♾️"]

ganhos_por_simbolo = {
        "🍒": (1, 4),
        "⏳": (2, 5),
        "⭐": (3, 6),
        "🍀": (3, 7),
        "💎": (4, 8),
        "♾️": (5, 10)
    }

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

    # REGISTRA USUÁRIO NOVO
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
    if saldo < 2:
        await ctx.send(f"❌ | {ctx.author.mention}, você precisa de pelo menos **2 escoltes** para jogar. Seu saldo atual: `{saldo}`.")
        return

    # COBRA 2 ESCOLTES
    data[user_id]["escolte"] -= 2
    save_database(data)

    # INÍCIO DA ANIMAÇÃO
    rodando = ["🔄", "🔃", "🔁"]
    mensagem = await ctx.send(f"🎰 | {ctx.author.mention} puxou a alavanca...\n\n```\n🎰 [🔄 | 🔄 | 🔄]\n```")

    # SIMULAÇÃO DO GIRO COM 10 ATUALIZAÇÕES
    for _ in range(6):
        girando = f"🎰 [ {random.choice(bet_symbols)} | {random.choice(bet_symbols)} | {random.choice(bet_symbols)} ]"
        await mensagem.edit(content=f"{ctx.author.mention} girando a roleta...\n\n```\n{girando}\n```")
        await asyncio.sleep(0.3)

    # RESULTADO FINAL
    slot1 = random.choice(bet_symbols)
    slot2 = random.choice(bet_symbols)
    slot3 = random.choice(bet_symbols)

    final = f"""
🎰 | {ctx.author.mention} girou a roleta!

```fix
╔════════════════╗
║  {slot1} | {slot2} | {slot3}  ║
╚════════════════╝
```
"""

    if slot1 == slot2 == slot3:
        ganho = ganhos_por_simbolo[slot1][1]  # Trinca
        data[user_id]["escolte"] += ganho
        final += f"\n💰 Você ganhou **{ganho} escoltes**!"
    elif slot1 == slot2 or slot2 == slot3 or slot1 == slot3:
        # Identifica o símbolo do par
        if slot1 == slot2 or slot1 == slot3:
            simbolo_par = slot1
        else:
            simbolo_par = slot2
        ganho = ganhos_por_simbolo[simbolo_par][0]  # Par
        data[user_id]["escolte"] += ganho
        final += f"\n✨ PAR encontrado ({simbolo_par}{simbolo_par})! Você ganhou **{ganho} escoltes**!"
    else:
        final += "\n😢 Nenhuma combinação. Tente novamente!"

    final += f"\n\n💰 | Saldo atual: `{data[user_id]['escolte']}` escoltes."

    save_database(data)
    await mensagem.edit(content=final)

@bot.command()
async def regras(ctx):
    regras_texto = f"""
🎰 **COMO FUNCIONA O SLOT VEGAS** 🎰

**COMO JOGAR**
Use `!vegas` para girar a roleta. Custa **2 escoltes** por rodada.

**OBJETIVO**
Tente conseguir 2 ou 3 símbolos iguais para ganhar mais escoltes.

**VALORES POR SÍMBOLO**
Cada símbolo tem um valor. Quanto mais vezes ele aparece, mais você ganha:

🍒🍒 = +1 | 🍒🍒🍒 = +4  
⏳⏳ = +2 | ⏳⏳⏳ = +5  
⭐⭐ = +2 | ⭐⭐⭐ = +6  
🍀🍀 = +2 | 🍀🍀🍀 = +7  
💎💎 = +3 | 💎💎💎 = +8  
♾️♾️ = +4 | ♾️♾️♾️ = +10


**REGRAS**
- Precisa ter **pelo menos 2 escoltes** pra jogar.

Boa sorte! 🍀
"""
    await ctx.send(regras_texto)

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
