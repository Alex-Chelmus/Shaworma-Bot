import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import subprocess
import socket 

conversatii_active = {}
meniu = {
    'Carne': ('pui', 'vita', 'mixt'),
    'Garnitura': ('cartofi', 'orez'),
    'Sos': ('ketcup', 'maioneza', 'curry', 'tzatziki'),
    'Legume': ('castraveti', 'varza', 'ceapa', 'patrunjel')
}


def este_valid(opt, categorie):
    return opt.lower() in meniu.get(categorie, [])


class ShawormaBot(commands.Bot):
    def __init__(self, *, intents):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.add_command(self.easter_egg)

    async def on_ready(self):
        print(f'{self.user} s-a conectat la Discord!')

    async def on_member_join(self, member):
        canal = self.get_welcome_channel(member.guild)
        if canal:
            mesaj = self.genereaza_mesaj_bun_venit(member)
            await canal.send(mesaj)

    def get_welcome_channel(self, guild):
        return discord.utils.get(guild.text_channels, name='comanda_shaworma')

    def genereaza_mesaj_bun_venit(self, member):
        return f'Ooo, tatii, {member.mention}, ai venit la shawormaaa'

    async def on_message(self, message):
        if message.author == self.user:
            return

        user_id = message.author.id

        if message.content.lower() == 'anulează comanda':
            if user_id in conversatii_active:
                del conversatii_active[user_id]
                await message.channel.send("Comanda ta a fost anulată, tati. Poți începe din nou oricând!")
            else:
                await message.channel.send("Nu ai nicio comandă activă, tati.")
            return

        if user_id in conversatii_active:
            etapa = conversatii_active[user_id]["etapa"]
            etapa_handlers = {
                "asteptare_confirmare_sau_meniu": self.handle_asteptare_confirmare_sau_meniu,
                "asteptare_carne": self.handle_asteptare_carne,
                "asteptare_garnish": self.handle_asteptare_garnish,
                "asteptare_sos1": self.handle_asteptare_sos1,
                "asteptare_sos2": self.handle_asteptare_sos2,
                "asteptare_legume1": self.handle_asteptare_legume1,
                "asteptare_legume2": self.handle_asteptare_legume2,
            }

            if etapa in etapa_handlers:
                await etapa_handlers[etapa](message, user_id)

            return

        if message.content.lower() == 'vreau sa comand':
            conversatii_active[user_id] = {"etapa": "asteptare_confirmare_sau_meniu"}
            await message.channel.send("Da tati, stii ce vrei deja sau iti dau meniul?")
            return

        if message.content.lower() == 'cu de toate':
            conversatii_active.pop(user_id, None)
            await message.channel.send(
                f"Gata tati, te așteaptă o shaworma caldă cu:\n"
                f"- Carne: {', '.join(meniu['Carne'])}\n"
                f"- Garnitură: {', '.join(meniu['Garnitura'])}\n"
                f"- Sosuri: {', '.join(meniu['Sos'])}\n"
                f"- Legume: {', '.join(meniu['Legume'])}"
            )
            return

        if message.content.lower() == 'porneste jocul':
            cale_joc = r"C:\Users\alexc\1. Scoala\2. An II\Semestrul II\1. Phyton\3. Proiect\POO\space.py"
            hostname = socket.gethostname()
            ip_adresa = socket.gethostbyname(hostname)
            await message.channel.send("Da tati, doar ca jocul ruleaza local doar pe laptop-ul cu adresa ip: "+ip_adresa)
            proc = subprocess.Popen([r"C:\Users\alexc\anaconda3\python.exe","-Xfrozen_modules=off",cale_joc])
            proc.wait()

        await self.process_commands(message)

    async def handle_asteptare_confirmare_sau_meniu(self, message, user_id):
        content = message.content.lower()
        if "meniu" in content:
            mesaj_meniu = "\n".join([f"{categorie}: {', '.join(opt)}" for categorie, opt in meniu.items()])
            await message.channel.send("Poftim tati, aici e meniul:\n" + mesaj_meniu)
        else:
            conversatii_active[user_id]["etapa"] = "asteptare_carne"
            await message.channel.send("Da tati, zi ce vrei vtm, acum ți-o fac! \nCe cărniță punem?")

    async def handle_asteptare_carne(self, message, user_id):
        content = message.content.lower()

        if content in ("nimic", "nu vreau", "fara", "nu merci"):
            conversatii_active[user_id]["carne"] = 'fara carne :('
        elif este_valid(content, "Carne"):
            conversatii_active[user_id]["carne"] = content
        else:
            await message.channel.send("Nu avem așa ceva tati, încearcă cu: pui, vita sau mixt")
            return

        conversatii_active[user_id]["etapa"] = "asteptare_garnish"
        await message.channel.send("Ce garnitură vrei la ea, tati?")

    async def handle_asteptare_garnish(self, message, user_id):
        content = message.content.lower()

        if content in ("nimic", "nu vreau", "fara", "nu merci"):
            conversatii_active[user_id]["garnish"] = 'fara garnitura :('
        elif este_valid(content, "Garnitura"):
            conversatii_active[user_id]["garnish"] = content
        else:
            await message.channel.send("Nu avem așa garnitură, încearcă cu: cartofi sau orez")
            return

        conversatii_active[user_id]["etapa"] = "asteptare_sos1"
        await message.channel.send("Bună alegere tati, da' ne mai trebuie sos. Hai, ia zi.")

    async def handle_asteptare_sos1(self, message, user_id):
        content = message.content.lower()

        if content in ("nimic", "nu vreau", "fara", "nu merci"):
            conversatii_active[user_id]["sos1"] = 'fara sos1 :('
        elif este_valid(content, "Sos"):
            conversatii_active[user_id]["sos1"] = content
        else:
            await message.channel.send("Nu avem sosul ăsta, încearcă cu: ketchup, maioneza, curry sau tzatziki")
            return

        conversatii_active[user_id]["etapa"] = "asteptare_sos2"
        await message.channel.send("Așa tati, începe să prindă contur, încă unu și terminăm cu asta.")

    async def handle_asteptare_sos2(self, message, user_id):
        content = message.content.lower()

        if content in ("nimic", "nu vreau", "fara", "nu merci"):
            conversatii_active[user_id]["sos2"] = 'fara sos2 :('
        elif este_valid(content, "Sos"):
            conversatii_active[user_id]["sos2"] = content
        else:
            await message.channel.send("Tati, nu avem sosul ăsta. Alege din ketchup, maioneza, curry sau tzatziki")
            return

        conversatii_active[user_id]["etapa"] = "asteptare_legume1"
        await message.channel.send("Gata sos-urile tati, urmează legumele!")

    async def handle_asteptare_legume1(self, message, user_id):
        content = message.content.lower()

        if content in ("nimic", "nu vreau", "fara", "nu merci"):
            conversatii_active[user_id]["legume1"] = 'fara legume1 :('
        elif este_valid(content, "Legume"):
            conversatii_active[user_id]["legume1"] = content
        else:
            await message.channel.send("Tati, nu avem leguma aia. Alege dintre: castraveti, varza, ceapa, patrunjel")
            return

        conversatii_active[user_id]["etapa"] = "asteptare_legume2"
        await message.channel.send("Bun, bun, încă o legumă să fim sănătoși tati!")

    async def handle_asteptare_legume2(self, message, user_id):
        content = message.content.lower()

        if content in ("nimic", "nu vreau", "fara", "nu merci"):
            legume2 = 'fara legume2 :('
        elif este_valid(content, "Legume"):
            legume2 = content
        else:
            await message.channel.send("Tati, n-avem leguma aia. Ultima șansă: castraveti, varza, ceapa, patrunjel")
            return

        data = conversatii_active[user_id]
        await message.channel.send(
            f"Gata tati, te așteaptă o shaworma caldă cu:\n"
            f"- Carne: {data['carne']}\n"
            f"- Garnitură: {data['garnish']}\n"
            f"- Sosuri: {data['sos1']}, {data['sos2']}\n"
            f"- Legume: {data['legume1']}, {legume2}"
        )
        del conversatii_active[user_id]

    @commands.command(name='easteregg')
    async def easter_egg(self, ctx):
        filepath = "easteregg.webp"
        if os.path.exists(filepath):
            await ctx.send("Tati, uite ce ți-am pregătit... ")
            await ctx.send(file=discord.File(filepath))
        else:
            await ctx.send("N-am găsit fișierul secret, tati ")


# Setup
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = ShawormaBot(intents=intents)
bot.run(TOKEN)
