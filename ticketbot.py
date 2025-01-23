import discord
from discord.ext import commands
import asyncio

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Muokkaa seuraavia muuttujia omien asetustesi mukaan
TICKET_CATEGORY_ID = 123456789012345678  # Kategoria, johon ticket-kanavat luodaan
STAFF_ROLE_ID = 123456789012345678  # Ylläpidon roolin ID
LOG_CHANNEL_ID = 123456789012345678  # Kanava, johon ilmoitukset avatuista ja suljetuista tiketeistä lähetetään

@bot.command(name="tiket")
async def create_ticket(ctx):
    # Tarkistetaan, onko käyttäjällä jo avoin tiketti
    existing_channel = discord.utils.get(ctx.guild.text_channels, name=f"tiket-{ctx.author.id}")
    if existing_channel:
        await ctx.send("Sinulla on jo avoin tiketti! Siirry kanavaan " + existing_channel.mention)
        return

    # Luodaan uusi tekstikanava tikettiä varten
    category = bot.get_channel(TICKET_CATEGORY_ID)
    ticket_channel = await ctx.guild.create_text_channel(
        name=f"tiket-{ctx.author.id}",
        category=category
    )

    # Asetetaan kanavan käyttöoikeudet: vain jäsen ja ylläpito pääsevät kanavalle
    await ticket_channel.set_permissions(ctx.guild.default_role, read_messages=False)
    await ticket_channel.set_permissions(ctx.author, read_messages=True, send_messages=True)
    
    # Asetetaan ylläpidolle pääsy kanavalle
    staff_role = ctx.guild.get_role(STAFF_ROLE_ID)
    if staff_role:
        await ticket_channel.set_permissions(staff_role, read_messages=True, send_messages=True)

    await ticket_channel.send(f"{ctx.author.mention} kiitos tiketin avaamisesta! Ylläpito auttaa sinua pian. Sulje tiketti kirjoittamalla `!sulje`.")
    await ctx.send(f"Tiketti avattu! Siirry kanavaan {ticket_channel.mention}.")

    # Lähetetään ilmoitus logikanavalle
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(f"Tiketti avattu: {ticket_channel.mention} (avaaja: {ctx.author.mention})")

@bot.command(name="sulje")
async def close_ticket(ctx):
    # Tarkistetaan, että komento annetaan ticket-kanavalla
    if not ctx.channel.name.startswith("tiket-"):
        await ctx.send("Tämä komento toimii vain ticket-kanavalla.")
        return

    # Vahvistus ennen kanavan sulkemista
    await ctx.send("Oletko varma, että haluat sulkea tiketin? Kirjoita `!vahvistasulku` vahvistaaksesi.")
    
    # Odottaa vahvistuskomentoa 30 sekunnin ajan
    def check(m):
        return m.content == "!vahvistasulku" and m.channel == ctx.channel and m.author == ctx.author

    try:
        await bot.wait_for("message", check=check, timeout=30)
        await ctx.send("Tämä tiketti suljetaan.")
        
        # Ilmoitus logikanavalle tiketin sulkemisesta
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(f"Tiketti suljettu: {ctx.channel.mention} (suljettu: {ctx.author.mention})")

        # Poistetaan kanava
        await ctx.channel.delete()

    except asyncio.TimeoutError:
        await ctx.send("Tiketin sulkeminen peruttu, koska vahvistusta ei saatu.")

# Korvaa tämä botin tokenilla
bot.run('YOUR_BOT_TOKEN')
