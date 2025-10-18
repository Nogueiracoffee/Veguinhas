import os
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import google.generativeai as genai
import asyncio

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
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_KEY)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- Inicializa modelo Gemini ---
model = genai.GenerativeModel("gemini-2.5-flash")

# --- Evento de inicialização ---
@bot.event
async def on_ready():
    print(f"🤖 Veguinhas conectado como {bot.user}")
    await bot.change_presence(activity=discord.Game(name="com a galera em Vegas ☕"))

# --- Função auxiliar para gerar resposta da Gemini ---
def gerar_resposta_sync(prompt):
    try:
        chat = model.start_chat(
            history=[
                {"role": "user", "parts": "Você é Veguinhas, bot simpático e criativo da comunidade Vegas Machine. Fale com naturalidade e humor leve."}
            ]
        )
        resposta = chat.send_message(prompt)
        return resposta.text
    except Exception as e:
        print(f"Erro Gemini: {e}")
        return "Ops! Tive um problema pra responder, tenta de novo ☕"

async def gerar_resposta(prompt):
    return await asyncio.to_thread(gerar_resposta_sync, prompt)

# --- Comando !ia ---
@bot.command()
async def ia(ctx, *, pergunta):
    await ctx.channel.typing()
    resposta_texto = await gerar_resposta(pergunta)
    await ctx.send(resposta_texto)

# --- Comando !falar ---
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

        resposta_texto = await gerar_resposta(texto_usuario)
        await message.reply(resposta_texto)

    await bot.process_commands(message)

bot.run(DISCORD_TOKEN)
