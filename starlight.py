import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands

import json
import os
import random
from dotenv import load_dotenv

import fonctions as F
from keep_alive import keep_alive

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

# S'INSCRIRE

@bot.tree.command(name = "inscription", description = "S'inscrire dans la base.")
async def inscription(interaction : discord.Interaction):
    
    joueur = str(interaction.user.id)

    with open("rolls.json", "r", encoding="utf-8") as fichier:
        data = json.load(fichier)
        
    data[joueur] = {"argent" : 0, "ticket" : 0, "collection" : [], "roue" : 0, "dortoir" : []}
    
    with open("rolls.json", "w", encoding="utf-8") as fichier:
        json.dump(data, fichier)
        
    await interaction.response.send_message(f"Vous êtes à présent inscrit(e) dans la base. Voici votre ID : `{joueur}`.", ephemeral = True)

# LANCER LA ROUE DES CONSÉQUENCES

@bot.tree.command(name = "roue", description = "Lancer la roue des conséquences.")
async def roue(interaction : discord.Interaction):
    
    joueur = str(interaction.user.id)
    
    with open("rolls.json", "r", encoding="utf-8") as fichier:
        data = json.load(fichier)
        
    with open("consequences.json", "r", encoding="utf-8") as fichier:
        consequences = json.load(fichier)
        
    data[joueur]["roue"] += 1
        
    n_tirage = data[joueur]["roue"]
    
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
    
    niveaux = list(consequences.keys())

    tirage_niveau = random.choices(niveaux, probabilites)[0]
    
    tirage_consequence = random.choice(consequences[tirage_niveau][1])
    
    embed = discord.Embed(title = "Roue des Conséquences", description = f"# {tirage_niveau} \n ### ▫️ {tirage_consequence} \n-# Les conséquences marquées par `W-` s'appliquent aux Waifus et celles marquées par `J-`, au Joueur.", color = 0x5875cc)
    embed.set_image(url = consequences[tirage_niveau][0])
    embed.set_footer(text = "Gacha Harem", icon_url = interaction.guild.icon)
    
    await interaction.response.send_message(embed = embed)

# LANCER LA BANNIÈRE

class MenuBN(discord.ui.View):
    
    def __init__(self):
        super().__init__()
        self.value = None
      
    @discord.ui.button(label = "Afficher les taux de drops.", style = discord.ButtonStyle.green)
    async def bouton_taux(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        with open("bannieres.json", "r", encoding="utf-8") as fichier:
            bannieres = json.load(fichier)
            
        banniere = bannieres["1"]
        
        chaine = ""
        
        for key in banniere.keys():
            chaine += f"- **{key}** | {banniere[key][2]} | `{banniere[key][0]}` \n"
        
        embed = discord.Embed(title = "Taux de drops", description = chaine, color = 0xf2d6ae)
        embed.set_footer(text = "Gacha Harem", icon_url = interaction.guild.icon)
        
        await interaction.response.send_message(embed = embed, ephemeral = True)

@bot.tree.command(name = "bannière", description = "Invoquer dans la bannière")
@app_commands.choices(vedette = [Choice(name = "Phrolova", value = 1)])
async def banniere(interaction : discord.Interaction, vedette : Choice[int]):
    
    joueur = str(interaction.user.id)
    
    with open("rolls.json", "r", encoding="utf-8") as fichier:
        data = json.load(fichier)
        
    with open("bannieres.json", "r", encoding="utf-8") as fichier:
        bannieres = json.load(fichier)
        
    if data[joueur]["ticket"] == 0:
        
        await interaction.response.send_message("Vous n'avez pas assez de tickets.")
        
    else:
        banniere = bannieres[str(vedette.value)]
    
        elements = list(banniere.keys())
        probabilites = [banniere[k][0] for k in banniere.keys()]

        tirage_banniere = random.choices(elements, probabilites)[0]
        
        data[joueur]["ticket"] -= 1
        
        if tirage_banniere not in data[joueur]["collection"]:
            data[joueur]["collection"].append(tirage_banniere)
            
        else:
            data[joueur]["argent"] += F.argent_doublon(banniere[tirage_banniere][1], banniere[tirage_banniere][2])

        with open("rolls.json", "w", encoding="utf-8") as fichier:
            json.dump(data, fichier)
        
        embed = discord.Embed(title = f"Bannière - {elements[0]}", description = f"# {tirage_banniere} \n### _Type : {banniere[tirage_banniere][1]}_ \n### _Rareté : {banniere[tirage_banniere][2]}_ \n### _Taux de drop : {banniere[tirage_banniere][0]}_", color = 0x8575cc)
        embed.set_image(url = banniere[tirage_banniere][3])
        embed.set_footer(text = "Gacha Harem", icon_url = interaction.guild.icon)
        
        await interaction.response.send_message(embed = embed, view = MenuBN())

# AJOUTER DES TICKETS

@bot.tree.command(name = "ajouter-tickets", description = "Ajouter des tickets d'invocations à un joueur.")
@app_commands.default_permissions(administrator = True)
@app_commands.describe(membre = "Mentionnez le joueur.")
@app_commands.describe(nombre = "Entrez le nombre de tickets à ajouter.")
async def ajouter(interaction : discord.Interaction, membre : discord.Member, nombre : str):
    
    joueur = str(membre.id)
    
    nb = int(nombre)
    
    with open("rolls.json", "r", encoding="utf-8") as fichier:
        data = json.load(fichier)

    data[joueur]["ticket"] += nb
    
    with open("rolls.json", "w", encoding="utf-8") as fichier:
        json.dump(data, fichier)
    
    await interaction.response.send_message(f"`{nb}` tickets ont été ajouté à la collection de <@{joueur}>.", ephemeral = True)

# DONNER UN OBJET

@bot.tree.command(name = "donner-objet", description = "Donner un objet à un joueur.")
@app_commands.default_permissions(administrator = True)
@app_commands.describe(membre = "Mentionnez le joueur.")
@app_commands.describe(objet = "Entrez le nom de l'objet à donner.")
async def donner(interaction : discord.Interaction, membre : discord.Member, objet : str):
    
    joueur = str(membre.id)
        
    with open("rolls.json", "r", encoding="utf-8") as fichier:
        data = json.load(fichier)

    data[joueur]["collection"].append(objet)
    
    with open("rolls.json", "w", encoding="utf-8") as fichier:
        json.dump(data, fichier)
    
    await interaction.response.send_message(f"L'objet `{objet}` a été ajouté à la collection de <@{joueur}>.", ephemeral = True)

# AFFICHER LA COLLECTION

@bot.tree.command(name = "collection", description = "Afficher la collection.")
async def collection(interaction : discord.Interaction):
    
    joueur = str(interaction.user.id)
    
    with open("rolls.json", "r", encoding="utf-8") as fichier:
        data = json.load(fichier)
        
    with open("bannieres.json", "r", encoding="utf-8") as fichier:
        bannieres = json.load(fichier)
    
    col = data[joueur]["collection"]
    
    personnages, mutations, kinks, decors = [], [], [], []
    
    for key in bannieres.keys():
        banniere = bannieres[key]
        for el in col:
            if banniere[el] == "Personnage":
                personnages.append(el)
            elif banniere[el] == "Mutation":
                mutations.append(el)
            elif banniere[el] == "Kink":
                kinks.append(el)
            else:
                decors.append(el)

    embed = discord.Embed(title = "Collection", description = f"**Argent :** `{data[joueur]["argent"]}`, **Tickets d'invocation :** `{data[joueur]["ticket"]}`", color = 0xe8a738)
    embed.add_field(name = "Personnages", value = "- " + '\n- '.join(personnages), inline = False)
    embed.add_field(name = "Mutations", value = "- " + '\n- '.join(mutations), inline = False)
    embed.add_field(name = "Kinks", value = "- " +  '\n- '.join(kinks), inline = False)
    embed.add_field(name = "Décors", value = "- " + '\n- '.join(decors), inline = False)
    embed.set_footer(text = "Gacha Harem", icon_url = interaction.guild.icon)
    
    await interaction.response.send_message(embed = embed)

# GÉRER LES COMBATS

@bot.tree.command(name = "gérer-combats", description = "Gérer les combats dans les étages.")
@app_commands.default_permissions(administrator = True)
@app_commands.choices(action = [
    Choice(name = "Attaque basique", value = 1),
    Choice(name = "Défense", value = 2),
    Choice(name = "Pouvoir 1", value = 3),
    Choice(name = "Pouvoir 2", value = 4)
    ])
@app_commands.describe(action = "Sélectionner l'action qui la Waifu va réaliser.")
@app_commands.describe(dgt = "Entrez le nombre de dégâts que la Waifu va infliger ou risquer de perdre.")
@app_commands.describe(pv = "Entrez le nombre de points de vie que la Waifu ou la Goule possède.")
async def gerer(interaction : discord.Interaction, action : Choice[int], dgt : str, pv : str):
    
    dgt, pv = int(dgt), int(pv)
    inf = pv - dgt
    
    if action.value == 1 or action.value == 4:
        
        if inf <= 0:
            await interaction.response.send_message(f"La Waifu a infligé {dgt} dégâts à la Goule. La Goule est éliminée.")
        else:
            await interaction.response.send_message(f"La Waifu a infligé {dgt} dégâts à la Goule. Il reste {inf} PV à la Goule.")
    
    elif action.value == 2:
        
        if inf <= 0:
            await interaction.response.send_message(f"La Waifu a subit {dgt} dégâts. Elle est éliminée.")
        else:
            await interaction.response.send_message(f"La Waifu a subit {dgt} dégâts. Il lui reste {inf+(dgt/2)} PV.")
            
    else:
        
        pass

# AFFICHER LE DORTOIR

@bot.tree.command(name = "dortoir", description = "Afficher le dortoir.")
async def dortoir(interaction : discord.Interaction):
    
    joueur = str(interaction.user.id)
    
    with open("rolls.json", "r", encoding="utf-8") as fichier:
        data = json.load(fichier)
    
    dor = data[joueur]["dortoir"]
    
    embeds = []
    
    for i in range(len(dor)):
        
        lit = dor[i]
        
        embed = discord.Embed(title = f"Lit n°{i+1}", description = f"***{lit["waifu"]}***", color = 0xf21658)
        embed.add_field(name = "Niveau", value = f"`{lit["waifu"]}`")
        embed.add_field(name = "Kinks", value = f"`{lit["kinks"]}`")
        embed.add_field(name = "Boosts", value = f"`{lit["boosts"]}`")
        embed.add_field(name = "Comportement", value = f"`{lit["comportement"]}`")
        embed.add_field(name = "Lien émotionnel", value = f"`{lit["lien"]}`")
        embed.add_field(name = "Personnalisation", value = f"`{', '.join(lit["personnalisation"])}`")
        
        embeds.append(embed)

    await interaction.response.send_message(embeds = embeds)

# COUCHER UNE WAIFU

@bot.tree.command(name = "coucher-waifu", description = "Assigner une Waifu à un lit.")
@app_commands.describe(numero = "Entrez le numéro du lit.")
@app_commands.describe(waifu = "Donnez la Waifu qui va dormir.")
async def coucher(interaction : discord.Interaction, numero : str, waifu : str):
    
    joueur = str(interaction.user.id)
    numero = int(numero)
    
    with open("rolls.json", "r", encoding="utf-8") as fichier:
        data = json.load(fichier)
    
    col = data[joueur]["collection"]
    dor = data[joueur]["dortoir"]
    
    with open("rolls.json", "w", encoding="utf-8") as fichier:
        json.dump(data, fichier)
    
    if waifu not in col:
        await interaction.response.send_message(f"Vous n'avez pas la Waifu `{waifu}`", ephemeral = True)
        
    else:
        dor[numero-1] = {"waifu" : waifu, "niveau" : 0, "kinks" : [], "boosts" : [], "comportement" : None, "lien" : 0, "personnalisation" : []}
        
# ACHETER UN LIT

@bot.tree.command(name = "acheter-lit", description = "Acheter un lit.")
async def acheter(interaction : discord.Interaction):
    
    joueur = str(interaction.user.id)
    
    with open("rolls.json", "r", encoding="utf-8") as fichier:
        data = json.load(fichier)
    
    prix = 500
    arg = data[joueur]["argent"]
    dor = data[joueur]["dortoir"]
    
    if arg-prix <= 0:
        await interaction.response.send_message("Vous n'avez pas assez d'argent pour acheter un lit.", ephemeral=True)
        
    else:
        arg -= prix 
        dor.append({"waifu" : None, "niveau" : 0, "kinks" : [], "boosts" : [], "comportement" : None, "lien" : 0, "personnalisation" : []})
    
        with open("rolls.json", "w", encoding="utf-8") as fichier:
            json.dump(data, fichier)
        
        await interaction.response.send_message("Vous avez bel et bien acheté un lit", ephemeral=True)

# AMÉLIORER UN LIT

@bot.tree.command(name = "ameliorer-lit", description = "Améliorer un lit.")
@app_commands.describe(numero = "Entrez le numéro du lit.")
async def ameliorer(interaction : discord.Interaction, numero : str):
    
    joueur = str(interaction.user.id)
    numero = int(numero)
    
    with open("rolls.json", "r", encoding="utf-8") as fichier:
        data = json.load(fichier)
    
    arg = data[joueur]["argent"]
    dor = data[joueur]["dortoir"]
    
    lit = dor[numero-1]
    niv = lit["niveau"]
    
    somme = (niv + 1) * 1000
    
    if arg-somme <= 0:
        await interaction.response.send_message("Vous n'avez pas assez d'argent pour améliorer le lit.", ephemeral=True)
        
    else:
        lit["niveau"] = niv + 1
        arg -= somme
        
        with open("rolls.json", "w", encoding="utf-8") as fichier:
            json.dump(data, fichier)
        
        await interaction.response.send_message(f"Votre lit est maintenant au niveau {lit["niveau"]}", ephemeral=True)

# ÉQUIPER UN ITEM
        
@bot.tree.command(name = "équiper-items", description = "Équiper à la Waifu un kink, un boost ou décorer son lit.")
@app_commands.choices(type = [
    Choice(name = "Kink", value = "kinks"),
    Choice(name = "Boost", value = "boosts"),
    Choice(name = "Décoration", value = "personnalisation")
    ])
@app_commands.describe(type = "Sélectionner le type de l'item.")
@app_commands.describe(item = "Entrez le nom de l'item à attribuer.")
async def equiper(interaction : discord.Interaction, numero : str, type : Choice[str], item : str):
    
    joueur = str(interaction.user.id)
    numero = int(numero)
    
    with open("rolls.json", "r", encoding="utf-8") as fichier:
        data = json.load(fichier)
    
    dor = data[joueur]["dortoir"]
    niv = data[joueur]["niveau"]

    lit = dor[numero-1]
    
    if type.value in ["kinks", "boosts"]:
        
        if niv == 0:
            await interaction.response.send_message("Niveau insuffisante.", ephemeral=True)
            
        elif niv == 1:
            lit[type.value][0] = item
            
        else:
            
            if len(lit[type.value]) < niv:
                lit[type.value].append(item)
                
            else:
                lit[type.value].append(item)
                lit[type.value].remove(lit[type.value][0])

    else:
        lit[type.value].append(item)

    with open("rolls.json", "w", encoding="utf-8") as fichier:
        json.dump(data, fichier)
        
    
    await interaction.response.send_message(f"La Waifu du lit {numero} a maintenant : {item} en plus.")

# MODIFIER LE COMPORTEMENT DE LA WAIFU

@bot.tree.command(name = "modifier-comportement", description = "Modifier le comportement de la Waifu.")
@app_commands.describe(numero = "Entrez le numéro du lit.")
@app_commands.describe(role = "Entrez son comportement (soumise, dominante, brat, yandere…).")
async def comportement(interaction : discord.Interaction, numero : str, role : str):
    
    joueur = str(interaction.user.id)
    numero = int(numero)
    
    with open("rolls.json", "r", encoding="utf-8") as fichier:
        data = json.load(fichier)
    
    dor = data[joueur]["dortoir"]
    lit = dor[numero-1]
    
    lit["comportement"] = role
    
    with open("rolls.json", "w", encoding="utf-8") as fichier:
        json.dump(data, fichier)
        
    await interaction.response.send_message(f"La Waifu du lit {numero} est maintenant : {role}.")

# GÉRER LA JALOUSIE

@bot.tree.command(name = "gérer-jalousie", description = "Gérer la jalousie des Waifus.")
@app_commands.default_permissions(administrator = True)
@app_commands.describe(coeur = "Entrez le nombre de coeur à ajouter ou retirer")
@app_commands.describe(numero = "Entrez le numéro du lit.")
@app_commands.describe(action = "Ajouter ou retirer ?")
@app_commands.describe(membre = "Mentionnez le joueur.")
async def jalousie(interaction : discord.Interaction, membre : discord.Member, numero : str, coeur : str, action : Choice[str]):
    
    joueur = str(membre.id)
    numero = int(numero)
     
    with open("rolls.json", "r", encoding="utf-8") as fichier:
        data = json.load(fichier)
    
    dor = data[joueur]["dortoir"]
    lit = dor[numero-1]
    
    lit["lien"] = lit["lien"] + (int(coeur) * action.value)
    
    with open("rolls.json", "w", encoding="utf-8") as fichier:
        json.dump(data, fichier)
        
    await interaction.response.send_message(f"Le lien émotionnel de la Waifu du lit {numero} de {membre} vaut maintenant : {lit["lien"]}.")

# METTRE EN ROUTE LE BOT

keep_alive()
bot.run(token = token)
