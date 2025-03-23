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
ARQUIVO_SALDO = "saldo_usuarios.txt"

# Variáveis do jogo
jogo_ativo = False
participantes = []
impostor = None
eliminados = []

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
# Comando para iniciar o jogo
@bot.command()
@commands.has_permissions(administrator=True)
async def iniciar(ctx):
    global jogo_ativo, participantes, impostor, eliminados

    if jogo_ativo:
        await ctx.send("O jogo já está em andamento!")
        return

    # Limpar dados do jogo
    participantes = []
    impostor = None
    eliminados = []

    # Obter todos os membros com o cargo @🏆 Rank
    cargo_rank = get(ctx.guild.roles, name="🏆 Rank")  # Ajuste o nome conforme necessário
    if cargo_rank is None:
        await ctx.send("Cargo @🏆 Rank não encontrado!")
        return

    # Adicionar todos os membros com o cargo @🏆 Rank à lista de participantes
    for membro in ctx.guild.members:
        if cargo_rank in membro.roles and not membro.bot:
            participantes.append(str(membro.id))

    if len(participantes) < 2:
        await ctx.send("Precisa de pelo menos 2 jogadores com o cargo @🏆 Rank para iniciar o jogo.")
        return

    # Escolher aleatoriamente o impostor entre os participantes
    impostor = random.choice(participantes)

    # Enviar mensagem privada para o impostor avisando sobre sua identidade
    impostor_membro = ctx.guild.get_member(int(impostor))
    await impostor_membro.send(f"Você é o **IMPOSTOR**! Seu objetivo é eliminar os outros jogadores sem ser descoberto. Boa sorte!")

    # Enviar mensagem pública informando que o jogo começou
    jogo_ativo = True
    await ctx.send(f"O jogo começou! O impostor é... alguém, mas não direi quem! O objetivo dos tripulantes é descobrir quem é o impostor!")

# Comando para o impostor eliminar alguém
@bot.command()
async def eliminar(ctx, membro: discord.Member):
    global impostor
    if not jogo_ativo:
        await ctx.send("O jogo não está ativo!")
        return

    if str(ctx.author.id) != impostor:
        await ctx.send("Você não é o impostor e não pode eliminar ninguém!")
        return

    if str(membro.id) not in participantes:
        await ctx.send("Este jogador não está no jogo!")
        return

    # Eliminar jogador
    participantes.remove(str(membro.id))
    eliminados.append(str(membro.id))
    await ctx.send(f"{membro.display_name} foi eliminado pelo impostor!")

# Comando para acusar o impostor
@bot.command()
async def acusar(ctx, membro: discord.Member):
    global impostor
    user_id = str(ctx.author.id)
    if user_id in eliminados:
        await ctx.send(f"{ctx.author.display_name}, você está eliminado do jogo!")
        return

    if str(membro.id) == impostor:
        saldo_usuarios[user_id] -= 1  # Custa 1 escolte para acusar
        saldo_usuarios[impostor] -= 1  # Impostor perde 1 escolte se for acusado corretamente
        salvar_saldo()
        await ctx.send(f"{ctx.author.display_name} acusou corretamente o impostor! {membro.display_name} perdeu 1 escolte!")
    else:
        saldo_usuarios[user_id] -= 1  # Custa 1 escolte para acusar
        salvar_saldo()
        await ctx.send(f"{ctx.author.display_name} acusou {membro.display_name} de ser o impostor, mas errou! Você perdeu 1 escolte!")


# Comando para o bot repetir uma mensagem (somente admin)
@bot.command()
@commands.has_permissions(administrator=True)
async def falar(ctx, *, mensagem):
    await ctx.message.delete()
    await ctx.send(mensagem)


# Rodar o bot
bot.run(TOKEN)
