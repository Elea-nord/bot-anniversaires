import discord
from discord.ext import commands, tasks
import json
import os
from datetime import datetime
from flask import Flask
from threading import Thread

TOKEN = os.getenv("MTQ5NTAzMDI3ODE0NDM5MzM4Ng.G-4W90.2yqfVzVGgmO2vdo_hv4gSy1ol_SwodKEEGiEHw")
CHANNEL_ID = int(os.getenv("1349001761821692026"))

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

FILE = "anniversaires.json"

# ----------- WEB SERVER (anti sleep) -----------
app = Flask('')

@app.route('/')
def home():
    return "Bot actif !"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ----------- DATA -----------
def load_data():
    if not os.path.exists(FILE):
        with open(FILE, "w") as f:
            json.dump([], f)
    with open(FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)

# ----------- COMMANDES -----------
@bot.group(invoke_without_command=True)
async def anniv(ctx):
    await ctx.send("Commandes : ajouter / supprimer / liste / aujourdhui")

@anniv.command()
async def ajouter(ctx, *, args):
    try:
        nom, date = args.rsplit(" ", 1)
        datetime.strptime(date, "%d-%m")
    except:
        return await ctx.send("❌ Format : !anniv ajouter Nom JJ-MM")

    data = load_data()
    data.append({"nom": nom, "date": date})
    save_data(data)

    await ctx.send(f"✅ {nom} ajouté ({date})")

@anniv.command()
async def supprimer(ctx, *, nom):
    data = load_data()
    new = [p for p in data if p["nom"].lower() != nom.lower()]

    if len(data) == len(new):
        return await ctx.send("❌ Introuvable")

    save_data(new)
    await ctx.send(f"🗑️ {nom} supprimé")

@anniv.command()
async def liste(ctx):
    data = load_data()
    if not data:
        return await ctx.send("📭 Vide")

    msg = "\n".join(f"- {p['nom']} : {p['date']}" for p in data)
    await ctx.send(f"📅 Anniversaires :\n{msg}")

@anniv.command()
async def aujourdhui(ctx):
    today = datetime.now().strftime("%d-%m")
    data = load_data()

    noms = [p["nom"] for p in data if p["date"] == today]

    if not noms:
        return await ctx.send("📭 Aucun aujourd’hui")

    await ctx.send("🎉 Aujourd’hui :\n" + "\n".join(noms))

# ----------- AUTO -----------
@tasks.loop(hours=24)
async def check_birthdays():
    today = datetime.now().strftime("%d-%m")
    data = load_data()

    noms = [p["nom"] for p in data if p["date"] == today]

    if noms:
        channel = bot.get_channel(1349001761821692026)
        if channel:
            await channel.send("🎉 Anniversaires :\n" + "\n".join(noms))

@bot.event
async def on_ready():
    print("Bot prêt")
    check_birthdays.start()

# ----------- START -----------
keep_alive()
bot.run(MTQ5NTAzMDI3ODE0NDM5MzM4Ng.G-4W90.2yqfVzVGgmO2vdo_hv4gSy1ol_SwodKEEGiEHw)
