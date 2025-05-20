import discord
from discord.ext import commands
import json
import random
import os

TOKEN = "MTMzMDM4NTEzNTkzMzMyNTM3Mw.Gx9HJU.2cuRPgW7ZYRjLqgk9-1iEfftdvzXgsQhof-2RE"

# Intents obrigatórios para funcionar corretamente
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Prefixo do bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Caminho do arquivo JSON onde o saldo dos usuários será salvo
DATABASE_FILE = "escolte_database.json"

# Emojis usados nos slots
bet_symbols = ["🐸", "🐵", "🐰", "🦊", "🐻", "🐼"]

# Valor mínimo para jogar
MIN_CREDITS_TO_PLAY = 3

# Função para carregar ou criar o banco de dados
def load_database():
	if not os.path.exists(DATABASE_FILE):
		with open(DATABASE_FILE, "w") as f:
			json.dump({}, f)
	with open(DATABASE_FILE, "r") as f:
		return json.load(f)

# Função para salvar o banco de dados atualizado
def save_database(data):
	with open(DATABASE_FILE, "w") as f:
		json.dump(data, f, indent=4)

# Comando principal do jogo
@bot.command(name="vegas")
async def vegas(ctx):
	user_id = str(ctx.author.id)  # ID único do usuário
	user_name = ctx.author.name   # Nome do usuário
	data = load_database()        # Carrega o banco

	# Se o usuário não estiver no banco, cria com 0 saldo e não deixa jogar
	if user_id not in data:
		data[user_id] = {
			"nome": user_name,
			"escolte": 0
		}
		save_database(data)
		await ctx.send(f"🛑 | {ctx.author.mention}, você foi registrado com **0 escoltes**. Peça para um admin adicionar saldo antes de jogar.")
		return

	saldo = data[user_id]["escolte"]

	# Se não tiver saldo suficiente
	if saldo < MIN_CREDITS_TO_PLAY:
		await ctx.send(f"💸 | {ctx.author.mention}, você precisa de pelo menos **{MIN_CREDITS_TO_PLAY} escoltes** para jogar. Saldo atual: **{saldo}**.")
		return

	# Gasta 3 créditos
	data[user_id]["escolte"] -= MIN_CREDITS_TO_PLAY

	# Sorteia os emojis
	slot1 = random.choice(bet_symbols)
	slot2 = random.choice(bet_symbols)
	slot3 = random.choice(bet_symbols)

	# Resultado dos slots
	resultado = f"🎰 | {slot1} | {slot2} | {slot3} | 🎰"

	# Verifica ganhos
	ganhou = False
	if slot1 == slot2 == slot3:
		data[user_id]["escolte"] += 20
		ganhou = True
		msg = f"🎉 {ctx.author.mention} tirou **3 iguais** e ganhou **20 escoltes!**"
	elif slot1 == slot2 or slot2 == slot3 or slot1 == slot3:
		data[user_id]["escolte"] += 15
		ganhou = True
		msg = f"😸 {ctx.author.mention} tirou **2 iguais** e ganhou **15 escoltes!**"
	else:
		msg = f"🙁 {ctx.author.mention}, você **não ganhou nada** dessa vez."

	# Salva o banco após o jogo
	save_database(data)

	# Mensagem final
	saldo_final = data[user_id]["escolte"]
	await ctx.send(f"{resultado}\n{msg}\n💰 Saldo atual: **{saldo_final} escoltes**")

# Comando para admin adicionar saldo
@bot.command(name="addescolte")
@commands.has_permissions(administrator=True)
async def add_escolte(ctx, membro: discord.Member, quantidade: int):
	user_id = str(membro.id)
	data = load_database()

	if user_id not in data:
		data[user_id] = {
			"nome": membro.name,
			"escolte": 0
		}

	data[user_id]["escolte"] += quantidade
	save_database(data)

	await ctx.send(f"✅ | {quantidade} escoltes adicionados para {membro.mention}. Novo saldo: **{data[user_id]['escolte']}**.")

# Evento para sinalizar que o bot está online
@bot.event
async def on_ready():
	print(f"✅ Bot online como {bot.user}")

# Inicie o bot com o seu token
bot.run("MTMzMDM4NTEzNTkzMzMyNTM3Mw.Gx9HJU.2cuRPgW7ZYRjLqgk9-1iEfftdvzXgsQhof-2RE")
