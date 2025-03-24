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

cargo_rank_nome = "Rank"  # Substitua pelo nome exato do cargo
cargo_rank = discord.utils.get(ctx.guild.roles, name=cargo_rank_nome)

if cargo_rank is None:
    await ctx.send(f"O cargo {cargo_rank_nome} não foi encontrado!")
    return
    # Verificar se há membros com o cargo @Rank
    for membro in ctx.guild.members:
        if cargo_rank in membro.roles and not membro.bot:
            participantes.append(membro.display_name)  # Usando display_name para mostrar o nome do membro

    # Verificar se a lista de participantes não está vazia
    if len(participantes) < 2:
        await ctx.send("Precisa de pelo menos 2 jogadores com o cargo @Rank para iniciar o jogo.")
        return

    # Log de depuração para verificar os participantes
    print(f"Participantes com o cargo @🏆 Rank: {participantes}")

    # Exibir os participantes no canal onde o comando foi executado
    participantes_list = "\n".join(participantes)
    await ctx.send(f"🎮 O jogo começou! 🎮\n\nOs participantes são:\n{participantes_list}")

    # Escolher aleatoriamente o impostor entre os participantes
    impostor = random.choice(participantes)

    # Enviar mensagem privada para o impostor avisando sobre sua identidade
    impostor_membro = ctx.guild.get_member(int(impostor))  # Buscar o membro no servidor
    if impostor_membro:
        await impostor_membro.send(f"Você é o **IMPOSTOR**! Seu objetivo é eliminar os outros jogadores sem ser descoberto. Boa sorte!")

    # Enviar mensagem pública informando que o jogo começou
    jogo_ativo = True
    await ctx.send(f"O jogo começou! O impostor é... alguém, mas não direi quem! O objetivo dos tripulantes é descobrir quem é o impostor!")

# Comando de eliminar um jogador
@bot.command()
async def eliminar(ctx, membro: discord.Member):
    global impostor, eliminados

    if not jogo_ativo:
        await ctx.send("O jogo ainda não foi iniciado.")
        return

    if membro.display_name == impostor:
        await ctx.send(f"{membro.display_name} foi eliminado! O impostor ganha essa rodada!")
        eliminados.append(membro.display_name)
        await finalizar_jogo(ctx, "impostor")
        return

    eliminados.append(membro.display_name)
    await ctx.send(f"{membro.display_name} foi eliminado!")

# Função para finalizar o jogo
async def finalizar_jogo(ctx, vencedor):
    global jogo_ativo
    jogo_ativo = False
    if vencedor == "impostor":
        await ctx.send("O impostor venceu! O jogo acabou.")
    elif vencedor == "tripulante":
        await ctx.send("Os tripulantes venceram! O impostor foi descoberto.")
    resetar_jogo()

# Função para resetar os dados do jogo
def resetar_jogo():
    global participantes, impostor, eliminados
    participantes = []
    impostor = None
    eliminados = []

# Comando para o bot repetir uma mensagem (somente admin)
@bot.command()
@commands.has_permissions(administrator=True)
async def falar(ctx, *, mensagem):
    await ctx.message.delete()
    await ctx.send(mensagem)

# Rodar o bot
bot.run(TOKEN)
