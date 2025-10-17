import os
import discord
from discord.ext import commands
from openai import OpenAI
from flask import Flask
from threading import Thread

# --- Servidor web para Koyeb ---
app = Flask('')

@app.route('/')
def home():
    return "Veguinhas tá online com a galera em Vegas ☕"

def run():
    app.run(host='0.0.0.0', port=8000)

Thread(target=run, daemon=True).start()
# -----------------------------------

# --- Configuração principal ---
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_KEY)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- Evento de inicialização ---
@bot.event
async def on_ready():
    print(f"🤖 Veguinhas conectado como {bot.user}")
    await bot.change_presence(activity=discord.Game(name="com a galera em Vegas ☕"))

# --- Comando !ia: conversa com IA ---
@bot.command()
async def ia(ctx, *, pergunta):
    await ctx.channel.typing()

    resposta = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é Veguinhas, bot simpático e criativo da comunidade Vegas Machine. Fale com naturalidade e humor leve."},
            {"role": "user", "content": pergunta}
        ]
    )

    await ctx.send(resposta.choices[0].message.content)

# --- Comando !falar: bot fala a mensagem enviada ---
@bot.command()
async def falar(ctx, *, mensagem):
    await ctx.message.delete()
    await ctx.send(mensagem)

# --- Responde automaticamente quando marcado ---
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message):
        await message.channel.typing()
        texto_usuario = message.content.replace(f"<@{bot.user.id}>", "").strip()

        if not texto_usuario:
            await message.reply("opa ☕ me chamou pra conversar?")
            return

        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é Veguinhas, o bot oficial da Vegas Machine. Fale de forma criativa, leve e com personalidade."},
                {"role": "user", "content": texto_usuario}
            ]
        )

        await message.reply(resposta.choices[0].message.content)

    await bot.process_commands(message)

bot.run(DISCORD_TOKEN)
