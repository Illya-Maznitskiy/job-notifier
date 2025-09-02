import os
from collections import defaultdict

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher


load_dotenv()


API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not API_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not set")

ADMIN_ID = os.getenv("ADMIN_ID")
if not ADMIN_ID:
    raise ValueError("ADMIN_ID not set")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# No PEP8 warnings about line length
# flake8: noqa
MEME_GIFS = [
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExa293a3lpNjA0cTJkemE0ZGlienhzZTdjbXltbTh2YXk1aG53a2ptcyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/gidMR0Kv3ljSivshKJ/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExd24xYWd2dmJvd2FtbXpxNnJ2dTBhbXE5ajFmamp3NmwxOXl5NTk1dCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/bNpLfNOskgvGIfKIZN/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcHliYnd2cmM2NHM5MHdobzNhMWd0cTluZmgzZjJxb21yMDBxanhjMCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/lEADCfIrDg5fMyb3ca/giphy.gif/media/l2JhB29QUPw6xD5eE/giphy.gif",
    "https://media1.tenor.com/m/vdtr2x9FopMAAAAd/wake-up-cat-cat-meme.gif",
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZXdoeDZkdXV6d2MweWIzbWZjYmpjaWdkeTFsYmxndDhiaDlqeW96ayZlcD12MV9naWZzX3NlYXJjaCZjdD1n/zaciDLCM6xGyi51kwB/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3eHNtMTB0YXZxYmthdDkydmQ3ZGg0eTNzYTNpdjJvcWJmengybzY5NyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/2RGhmKXcl0ViM/giphy.gif",
    "https://media1.tenor.com/m/vy3Hk2ADlaYAAAAd/stay-hard.gif",
    "https://media1.tenor.com/m/0bLK6asVSZYAAAAd/i-am-back-mother-fucker-david-goggins.gif",
    "https://media1.tenor.com/m/D8xkV7B7_-IAAAAC/motivation-motivational-quotes.gif",
    "https://media1.tenor.com/m/i5fhGSgFTmcAAAAd/mr-bean-thumbs-up.gif",
    "https://media.tenor.com/9oi-uh5ZeH0AAAAi/herve-apu.gif",
    "https://media1.tenor.com/m/eAwDugg8aBgAAAAd/kitty-meow.gif",
    "https://media1.tenor.com/m/KshIPrRS1aAAAAAd/cat-orange-cat.gif",
    "https://i.pinimg.com/originals/86/64/11/866411be17e4b33411a40cde77d57afa.gif",
]
READY_GIF_URLS = [
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExanZqMnl1NWNwdHlmcGg0cHZzbGtiZHJlNHpsYmtueHB6amJieTQ2bCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/xT39Db8zIOODTppk08/giphy.gif",
    "https://media1.tenor.com/m/RIxhUuakMdEAAAAd/ready-are-you-ready.gif",
    "https://media1.tenor.com/m/zgHjtVU_rocAAAAd/ac-dc-brian-johnson.gif",
    "https://media.tenor.com/YbOlajBHutcAAAAj/sports-sportsmanias.gif",
    "https://media1.tenor.com/m/GnKeRkk8OkMAAAAd/yes-excited.gif",
    "https://media1.tenor.com/m/90_rtIn6EWYAAAAd/ponke-ponkesol.gif",
    "https://media1.tenor.com/m/MWqd3aJwcHwAAAAC/s12.gif",
]

user_request_count = defaultdict(int)
