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
APPLIED_GIFS = [
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExa293a3lpNjA0cTJkemE0ZGlienhzZTdjbXltbTh2YXk1aG53a2ptcyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/gidMR0Kv3ljSivshKJ/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExd24xYWd2dmJvd2FtbXpxNnJ2dTBhbXE5ajFmamp3NmwxOXl5NTk1dCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/bNpLfNOskgvGIfKIZN/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcHliYnd2cmM2NHM5MHdobzNhMWd0cTluZmgzZjJxb21yMDBxanhjMCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/lEADCfIrDg5fMyb3ca/giphy.gif",
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
READY_VACANCY_GIFS = [
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExanZqMnl1NWNwdHlmcGg0cHZzbGtiZHJlNHpsYmtueHB6amJieTQ2bCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/xT39Db8zIOODTppk08/giphy.gif",
    "https://media1.tenor.com/m/RIxhUuakMdEAAAAd/ready-are-you-ready.gif",
    "https://media1.tenor.com/m/zgHjtVU_rocAAAAd/ac-dc-brian-johnson.gif",
    "https://media.tenor.com/YbOlajBHutcAAAAj/sports-sportsmanias.gif",
    "https://media1.tenor.com/m/GnKeRkk8OkMAAAAd/yes-excited.gif",
    "https://media1.tenor.com/m/90_rtIn6EWYAAAAd/ponke-ponkesol.gif",
    "https://media1.tenor.com/m/MWqd3aJwcHwAAAAC/s12.gif",
    "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExMXphZ2RzcnpydjVpdGtxMDJna3YzcTQxdmcyYmQyd2RpeG4yM2tteCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/gVsmn4qdyBn1Bra2tN/giphy.gif",
    "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExZDZ3aDFqczI4c2J2YThmMGllbmI3dG5kYzlwdHRpdTBsaW9kbm5kZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/GwbVjTKRkFgqs/giphy.gif",
    "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExYTV0aHM1NGo4ZnUwY3RnOHU0a3RuZXppZzhtNmhpM3c0b3Q3MHJ4NiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/d6UbuwWVKJHXO/giphy.gif",
    "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExdjlmOHA4c2phbm95ZmI4N2VyZnJoZ2UwcWFydXYweGxjb3BtcnpjdyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/liamKgDNyZi3C/giphy.gif",
    "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExOWU1bXZjcmwxOTczazdsenhqaG4xbThrY2xwa2doYmt2dm5xZHdwciZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/dsMFrxB2agKf6/giphy.gif",
    "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExY2p0ZGQ1b2NubzBpNzluenYwa3hoY3YyazE4cWxha3UxcTNsY3Q5eCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/YRtLgsajXrz1FNJ6oy/giphy.gif",
    "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExYmY0c2N1NjYydjI3MjNrdzRvZTh6MGFpYXRjZmI4dXY5bWpyaXFpZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/SS40oFiyppsHhvClo2/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMjY3YWhneDZnZnZpcGJ1YmhpN2F1a2lsNnE4d255YjExMnhuNTN6OCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/UqpjszfpiOiLA0L5le/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3M3E2ZjFmd3R3ajFnNmlqbnBhZ2JqbjFyc2RxanprcGRzb2R5emZkMiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/d2ZjLyU3TL67zc40/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3dnE1bGZhMDQ5Mzg3Nno0eGdyZzcyOGEzdXFqeWg1d2tvYWl2OXh6eiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/bPCwGUF2sKjyE/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3cXU0dXVlanhpN3Exanlic3BpbzZzOWtiZ3FpaHExaXN5d3IwYmU5MyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/7racSXDMsY4fK/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3cXU0dXVlanhpN3Exanlic3BpbzZzOWtiZ3FpaHExaXN5d3IwYmU5MyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/9GIE4bg4EV7UYFeP5B/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3ZmNhZnphdml0aTk1OTI2Z2I5ODE4ZGtuMGJsZ2Q0NWJhZTM3dnNsMCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/128Ygie2wLdH5m/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3cjZ5Y2ZzdDdmbWIzMzBxZ3Zsa25oa2V3OHd6c2xyaWF3dmdxa3N3MSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/9rtpurjbqiqZXbBBet/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3a294cHJnMGFjYmlraHRrYnJlZ2g3dHB5bGoxbHJoeXFnNHdydnR6YyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/KA593kO0JvXMs/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3N2VhNmdlM29la2Rwcjc3enh2aHBrYzlsbjUzeTZmbTcwOGF2cms0MyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/pqCxL43whDKzS/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3ZHA2N3ZlNGc3dzJrcnZqZmI5aGZlcmdzeng1b293c2pjZGtuMmw0eCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/2RiU1RUjyh4C4/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3amVqMHA2eHkzcDRoZjU4Nm5yZWR3dHMwNGx6Y3N2cDZlbGtmcmY1dSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/PvvSfSDFoAL5e/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3NnZqZWdibnlpOXQyMDJ2bWhhMzNnNmpuaWttZGJuYzE0N3pzM25peiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/cFdHXXm5GhJsc/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3NnZqZWdibnlpOXQyMDJ2bWhhMzNnNmpuaWttZGJuYzE0N3pzM25peiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/wpoLqr5FT1sY0/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3eHhtcjNycDBleHY1cmcwY2dybDF3d2E0MzFxZDg5dHFlcnhhamthcCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/11JTxkrmq4bGE0/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3eHhtcjNycDBleHY1cmcwY2dybDF3d2E0MzFxZDg5dHFlcnhhamthcCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/ThrM4jEi2lBxd7X2yz/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3cmUydGV1Nmo3dHd0MXFuMTAxMXJ5cGI4MnZndHo5eTE0NDczbWoyeiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/ue5ZwFCaxy64M/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3cmUydGV1Nmo3dHd0MXFuMTAxMXJ5cGI4MnZndHo5eTE0NDczbWoyeiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/QqkRs73FlKO52/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3eWVpdmR4MWV1cHhzNzV4NThsZndjd29uZmdndDAwb2c3OGV2NGRrMSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/VbnUQpnihPSIgIXuZv/giphy.gif",
]

NOTIFICATION_MESSAGES = [
    "Hey, check new jobs! Try /refresh 👀",
    "Latest jobs? Run /refresh 😎",
    "Don’t miss jobs! Use /refresh 🔥",
    "Don’t snooze! Use /refresh 😴",
    "Opportunities are waiting! /refresh ✨",
    "Jobs incoming! /refresh 🚀",
]
NOTIFICATION_GIFS = [
    "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExZDlrOWdqMmpicnJ0cGpidTd4Mmd0MHBkbjlnZ3Y3OGluaW0xbmg4eCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/fUQ4rhUZJYiQsas6WD/giphy.gif",
    "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExc3lvMWVqOTF5ZGxscXJsZm4zOWp5azdtNDZ3c3FvNWFzNzl5bm5oMiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/tHIRLHtNwxpjIFqPdV/giphy.gif",
    "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExczl4MXk4dTJsdmhpMTJyNnRtbDkxcTE1dWgxbHA0b2QwZ3d5cDdzcyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/DYH297XiCS2Ck/giphy.gif",
    "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExOGlrZnBjZ3NkZHR6NWpqZG40YmpobnFqcGJkODgwMWJqMjVjZmZ6NSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/l0GtHIM5EbawwbX1K/giphy.gif",
    "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExaWJ1M2kxYzZpOTJ4dTAybXNtc2RiMXBsYzdmcmEwZzFtdDBybDRlNCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QBd2kLB5qDmysEXre9/giphy.gif",
    "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExbGV2aWd5ams2OHBxMndxOGE2ZzgwNm1nd2tidXA3NmwzMHlsZ3BrbyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/sthmCnCpfr8M8jtTQy/giphy.gif",
    "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExa2Z4M3NwNnFoZ253c2dhZjBvanV5YWNvc2F2aHM2a2RobDM2OTEyNCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QPQ3xlJhqR1BXl89RG/giphy.gif",
    "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExZTl0aG9zcW85eW14cGRlbnpjamQ0ajBtMHZxZG43NmV3c2N0anNvbiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/GiWEowj3nQv9C/giphy.gif",
    "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExZ2JqMHMyOTE1a3liZXl5NHR4emQwNmQ2ZHRrMnVrbTVvOTRnM2Z3biZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/jZAwc1FZ4TednLkWwu/giphy.gif",
    "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExNXZjanB2Y211Z2w1bTYwcHY2aDNqN3l4ZWp4YjE0NjJpOGVjdTFrYSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/xT9IgG50Fb7Mi0prBC/giphy.gif",
    "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExNWRiMXB4bjludng4NGt2Y2gxc3I0b3pweWMxdXRqYmVrYTYyanJ3YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/IThjAlJnD9WNO/giphy.gif",
    "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExbGE0cXhxeWk1c3J0YzI0bGp4eG1rczJlY24wd3FlaDRybWhkNTBjdCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/imI7Kn0Tbi80w/giphy.gif",
]

# Max jobs per user per /refresh
MAX_FILTERED_JOBS = 1000

user_request_count = defaultdict(int)
