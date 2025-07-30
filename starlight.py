import discord
from discord import app_commands
from discord.ext import commands

import json
import os
import random
from dotenv import load_dotenv
from keep_alive import keep_alive

print("""
       _____ _             _ _       _     _   
      / ____| |           | (_)     | |   | |  
     | (___ | |_ __ _ _ __| |_  __ _| |__ | |_ 
      \___ \| __/ _` | '__| | |/ _` | '_ \| __|
      ____) | || (_| | |  | | | (_| | | | | |_ 
     |_____/ \__\__,_|_|  |_|_|\__, |_| |_|\__|
                                __/ |          
                               |___/           
      """)

# DÉFINIR LE CHEMIN D'ACCÈS

chemin = os.path.join(os.path.dirname(__file__))

os.chdir(chemin)

# CHERCHER LE TOKEN

load_dotenv()

token = os.getenv('DISCORD_TOKEN')

# PARAMÉTRER LE BOT

intents = discord.Intents().all()

intents.guilds = True
intents.members = True
intents.message_content = True
intents.presences = True
intents.typing = False

bot = commands.Bot(command_prefix = "§", intents = intents, description = "Bot développé par Augustus Production")

tree = app_commands.CommandTree(discord.Client(intents = intents))

# MONTRER QUE LE BOT EST CONNECTÉ

@bot.event
async def on_ready():
    
    print("\n---------------------- Le bot est en ligne ----------------------\n")
    print("<> Nom d'utilisateur :", bot.user.name)
    print("<> ID :", bot.user.id)
    
    await bot.change_presence(activity = discord.Game(name = "Gacha Harem"))
    
    try:
        synced = await bot.tree.sync()
        print(f"\n-------------- {len(synced)} commandes ont été synchronisées ! --------------\n")
        
    except Exception as e:
        print(e)

# CRÉER UNE COMMANDE DE TEST

@bot.tree.command(name = "test", description = "Tester les slash commandes.")
@app_commands.default_permissions(administrator = True)
async def test(interaction : discord.Interaction):
    await interaction.response.send_message(f"Salut ! Tu viens d'utiliser une slash commande.", ephemeral = True)

# LANCER LA ROUE DES CONSÉQUENCES

@bot.tree.command(name = "roue", description = "Lancer la roue des conséquences.")
async def roue(interaction : discord.Interaction):
    
    joueur = str(interaction.user.id)
    
    with open("rolls.json", "r", encoding="utf-8") as fichier:
        data = json.load(fichier)
        
    data[joueur] = data.get(joueur, 0) + 1
        
    n_tirage = data[joueur]
    
    if 1 <= n_tirage <= 10:
        probabilites = [0.60, 0.35, 0.05]  
    elif 11 <= n_tirage <= 20:
        probabilites = [0.50, 0.40, 0.10]  
    elif 21 <= n_tirage <= 30:
        probabilites = [0.35, 0.45, 0.20]  
    elif 31 <= n_tirage <= 40:
        probabilites = [0.20, 0.40, 0.40]  
    elif 41 <= n_tirage <= 50:
        probabilites = [0.00, 0.00, 1.00]
        
    with open("rolls.json", "w", encoding="utf-8") as fichier:
        json.dump(data, fichier)
    
    niveaux = ["🔹 CONSÉQUENCES COURANTES", "🔸 CONSÉQUENCES RARES", "🔺 CONSÉQUENCES TRÈS RARES & DÉFINITIVES"]

    Consequences = {
        "🔹 CONSÉQUENCES COURANTES" : ["W- Mutation sauvage incontrôlée", "W- Blocage émotionnel", "W- Brisure mentale (refus d'obéir)", "W- Altération de voix ou de langage (ne parle plus qu'en gémissements, langage codé, etc.)", "W- Perte de l'accès à certains kinks", "W- RP forcé en petplay ou maid pendant 24h", "J- Parole inversée", "J- Perte du langage", "J- Fétiche imposé pour 48h", "J- Soumission forcée"], 
        "🔸 CONSÉQUENCES RARES" : ["W- Auto-mutilation (perte de pv toutes les heures)", "W- Rejet de toute présence du maître(sse) du harem → ne supporte plus que les waifus dans le harem", "W- Hystérie nocturne : attaque une autre waifu au hasard chaque nuit", "W- Mutation non sexuelle (ailes, corne, bras en liane…) non réversible", "W- Appartenance perdue : elle “appartient” désormais à une autre joueuse/joueur", "J- Transformation en animal (RP obligatoire : neko, bunny, etc.)", "J- Interdiction de toucher certaines waifus", "J- Soumission magique : certaines waifus peuvent te donner des ordres en combat"], 
        "🔺 CONSÉQUENCES TRÈS RARES & DÉFINITIVES" : ["Effets permanents", "Humiliation totale", "Transformation sans retour"]
    }
    
    tirage_niveau = random.choices(niveaux, probabilites)[0]
    
    tirage_consequence = random.choice(Consequences[tirage_niveau])
    
    embed = discord.Embed(title = "Roue des Conséquences", description = f"# {tirage_niveau} \n ### ▫️ {tirage_consequence} \n-# Les conséquences marquées par `W-` s'appliquent aux Waifus et celles marquées par `J-`, au Joueur.", color = 0x5875cc)
    embed.set_image(url = "https://i.imgur.com/hBDqnh4.jpeg")
    embed.set_footer(text = "Gacha Harem", icon_url = interaction.guild.icon)
    
    await interaction.response.send_message(embed = embed)

# METTRE EN ROUTE LE BOT

keep_alive()
bot.run(token = token)
