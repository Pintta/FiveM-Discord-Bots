import discord
from discord.ext import commands, tasks
import requests

# Asetetaan botti ja intents
intents = discord.Intents.default()
intents.members = True  # Tarvitaan jäsenten liittymisen havaitsemiseen
bot = commands.Bot(command_prefix="!", intents=intents)

# FiveM-palvelimen IP ja portti (korvaa oikeilla tiedoilla)
FIVEM_SERVER_IP = "127.0.0.1"  # Korvaa oikealla IP-osoitteella
FIVEM_SERVER_PORT = "30120"  # Korvaa oikealla portilla
STATUS_CHANNEL_ID = 123456789012345678  # Kanava, johon botti ilmoittaa palvelimen tilan
ROLE_ID = 123456789012345678  # Rooli, joka lisätään uusille jäsenille
WELCOME_CHANNEL_ID = 123456789012345678  # Tervetulokanavan ID
RULES_CHANNEL_ID = 123456789012345678  # Sääntökanavan ID

# Komento, joka tarkistaa FiveM-palvelimen tilan ja pelaajamäärän
@bot.command(name="serverstatus")
async def serverstatus(ctx):
    try:
        # Haetaan palvelimen tiedot
        response = requests.get(f"http://{FIVEM_SERVER_IP}:{FIVEM_SERVER_PORT}/players.json")
        player_data = response.json()
        player_count = len(player_data)  # Pelaajien määrä
        
        await ctx.send(f"FiveM-palvelin on **päällä** ja siellä on **{player_count}** pelaajaa.")
    except Exception as e:
        await ctx.send("Palvelin ei ole päällä tai tietoja ei voitu hakea.")

# Scheduled task joka tarkistaa palvelimen tilan 10 minuutin välein
@tasks.loop(minutes=10)
async def scheduled_server_status():
    channel = bot.get_channel(STATUS_CHANNEL_ID)
    try:
        # Hae tiedot palvelimelta
        response = requests.get(f"http://{FIVEM_SERVER_IP}:{FIVEM_SERVER_PORT}/players.json")
        player_data = response.json()
        player_count = len(player_data)
        
        await channel.send(f"FiveM-palvelin on **päällä** ja siellä on **{player_count}** pelaajaa.")
    except Exception as e:
        await channel.send("Palvelin ei ole päällä tai tietoja ei voitu hakea.")

# Uusien jäsenten toivotus ja roolin lisäys
@bot.event
async def on_member_join(member):
    # Lisää automaattisesti rooli jäsenelle
    role = member.guild.get_role(ROLE_ID)
    if role:
        await member.add_roles(role)
        print(f"Rooli {role.name} lisätty jäsenelle {member.name}")

        # Ilmoitus liittymisestä tervetulokanavalla
        welcome_channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
        if welcome_channel:
            await welcome_channel.send(f"Tervetuloa {member.mention}! Muistathan lukea säännöt kanavasta!")

# Kun botti käynnistyy, aloita ajastettu tehtävä
@bot.event
async def on_ready():
    scheduled_server_status.start()  # Käynnistä automaattinen tilan tarkastus
    print(f"{bot.user.name} on käynnissä ja tarkistaa palvelimen tilan säännöllisesti!")

# Sääntökanavan tarkistus: lisää rooli kun jäsen reagoi
@bot.event
async def on_raw_reaction_add(payload):
    if payload.channel_id == RULES_CHANNEL_ID and str(payload.emoji) == "✅":
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if member:
            role = guild.get_role(ROLE_ID)  # Automaattisesti lisättävä rooli
            if role:
                await member.add_roles(role)
                print(f"{member.name} kuittasi säännöt ja rooli {role.name} lisätty")

                # Ilmoita tervetulokanavalle, että jäsen hyväksyi säännöt
                log_channel = guild.get_channel(WELCOME_CHANNEL_ID)
                if log_channel:
                    await log_channel.send(f"Jäsen {member.mention} hyväksyi säännöt ja rooli {role.name} lisättiin.")

# Korvaa tämä botin tokenilla
bot.run('YOUR_BOT_TOKEN')
