import discord
import requests
import json
import time

client = discord.Client()

settings = json.loads(open("settings.json", "r").read())
channel = settings["channel_id"]
user = settings["user_id"]
token = settings["user_token"]
delay = settings["delay"]
newest_first = settings["newest_first"]

def search():
    sort = "desc" if newest_first else "asc"
    get = requests.get(f"https://discordapp.com/api/v8/channels/{channel}/messages/search"
                       f"?author_id={user}&include_nsfw=true&sort_by=timestamp&sort_order={sort}&offset=0",
                       headers={"Authorization": token})
    obj = json.loads(get.text)
    result = []
    if obj["total_results"] <= 0:
        return result
    for cluster in obj["messages"]:
        for msg in cluster:
            if msg["author"]["id"] != str(user):  # Ignore if author is not you
                continue
            mid = msg["id"]
            if mid not in result:  # Avoid duplicates
                result.append(mid)  # Appends message ID as string
    return result

def delete(mid):
    requests.delete(f"https://discordapp.com/api/v8/channels/{channel}/messages/{mid}",
                    headers={"Authorization": token})
    time.sleep(delay)
    
@client.event
async def on_message(message):
    if message.author == client.user and message.content.lower() == ",lol":
        global channel
        channel = message.channel.id
        global user
        user = client.user.id
        while True:
            messages = search()

            if len(messages) == 0:
                break

            for message in messages:
                delete(message)
client.run(token, bot=False)
