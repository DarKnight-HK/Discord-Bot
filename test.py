#imports
import json

import discord

import token1

from discord.ext import commands

from discord import File

from easy_pil import Editor, load_image_async, Font

from discord.ext.commands import has_any_role, CheckFailure

from discord import Member

#intents
intents = discord.Intents.all()


#bot object
client = commands.Bot(command_prefix="!",intents=intents, help_command=None)
#custom stuff
with open("custom_responses.json","r") as f:

  x = json.load(f)
with open("banned_words.json","r") as q:
  b= json.load(q)



#counting stuff
with open("count.json","r") as cnt_read:
    c = json.load(cnt_read)  


#prints when bot is ready
@client.event
async def on_ready():
    print(f"{client.user} is now running!")


#welcomes new users
@client.event
async def on_member_join(member: Member):
    channel = discord.utils.get(member.guild.text_channels, name="welcome")
    backgroud = Editor("pic1.jpg").resize((800,450)) 
    profile_image = await load_image_async(str(member.display_avatar))
    profile = Editor(profile_image).resize((150,150)).circle_image()
    poppins= Font.poppins(size=50,variant="bold")
    poppins_small = Font.poppins(size=25, variant="light")
    backgroud.paste(profile,(325,90))
    backgroud.ellipse((325,90), 150, 150, outline="white",stroke_width=5)
    backgroud.text((400,260), f"WELCOME TO {member.guild.name}", color="white",font=poppins, align="center")
    backgroud.text((400,325), f"{member.name}#{member.discriminator}", color="white", font=poppins_small, align="center")
    file = File(fp=backgroud.image_bytes, filename="pic1.jpg")
    await channel.send(f"HELLO {member.mention}! WELCOME TO {member.guild.name}")
    await channel.send(file=file)
@client.event
async def on_member_remove(member: Member):
    channel = discord.utils.get(member.guild.text_channels, name="goodbye")
    await channel.send(f"{member.name} has left the server, such a pussy!")

#responds to messages
@client.event
async def on_message(message):
    if message.author == client.user:
            return
    if not message.content.startswith(client.command_prefix):
        global x        
        p_message = message.content.lower()
        test = p_message.split()
        if message.author == client.user:
            return
        if p_message in b["banned words"]:
            await message.delete()
            await message.channel.send(f"{message.author.mention} this is your final warning STFU", delete_after = 5)
        else:
            for key in b["banned words"]:
                if key in test:
                    await message.delete()
                    await message.channel.send(f"{message.author.mention} this is your final warning STFU", delete_after = 5) 
        if p_message in x:
            response = x[p_message]
            await message.channel.send(response)
        else:   
            for key in x.keys():
                if key in test:
                    response = x[key]
                    await message.channel.send(response)
    #counting
        if message.channel.id == c["count_channel"]:
            if message.content.isdigit():
                if int(message.content) == (c["current_count"] + 1) and message.author.name != c["last_counted_user"]:
                    await message.add_reaction("✅")
                   
                    c["current_count"] += 1
                    c["last_counted_user"] = message.author.name
                    with open("count.json","w") as cnt_write:
                        json.dump(c, cnt_write, indent=2)
                else:
                    await message.add_reaction("❌")
                    cc= c["current_count"]
                    await message.channel.send(f"{message.author.mention} You fucking idiot, you ruined it at {cc +1 }, next number is 1")
                    c["current_count"] = 0
                    c["last_counted_user"] = ""
                    with open("count.json","w") as cnt_write:
                        json.dump(c, cnt_write, indent=2)




    await client.process_commands(message)
#reaction roles
@client.event
async def on_raw_reaction_add(payload):
    target_message_id = 1100468336569102388
    guild = client.get_guild(payload.guild_id)
    if payload.message_id != target_message_id:
        return
    if payload.emoji.name == "t2":
        role = discord.utils.get(guild.roles, name = "Average Guy")
        await payload.member.add_roles(role)
    if payload.emoji.name == "test":
        role = discord.utils.get(guild.roles, name = "Hacker")
        await payload.member.add_roles(role)
@client.event
async def on_raw_reaction_remove(payload):
    target_message_id = 1100468336569102388
    guild = client.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)
    if payload.message_id != target_message_id:
        return
    if payload.emoji.name == "t2":
        role = discord.utils.get(guild.roles, name = "Average Guy")
        await member.remove_roles(role)
    if payload.emoji.name == "test":
        role = discord.utils.get(guild.roles, name = "Hacker")
        await member.remove_roles(role)


    

#commands
@client.command()
@has_any_role("Debugger","Admin")
async def add(ctx):
    await ctx.send("Enter your question:")
    question = await client.wait_for('message', check=lambda m: m.author == ctx.author)
    await ctx.send("Enter the answer:")
    answer = await client.wait_for('message', check=lambda m: m.author == ctx.author)
    x[question.content.lower()] = answer.content.lower()

    with open("custom_responses.json", "w") as q:
        json.dump(x, q, indent=2)
    await ctx.send("added")
@add.error
async def add_error(ctx, error):
    if isinstance(error, CheckFailure):
        await ctx.send("You don't have the permissions to do that")

@client.command()
async def cmd_list(ctx):
    question_list = "\n".join(x.keys())
    
    embed = discord.Embed(title="List of availale commands/responses", description=question_list, color=0x00ff00)
    await ctx.send(embed=embed)


@client.command()
@has_any_role("Debugger","Admin")

async def remove_cmd(ctx):
    await ctx.send("Enter the command that you want to remove:")
    rm_cmd = await client.wait_for('message', check=lambda m: m.author == ctx.author)
    if rm_cmd.content in x.keys():
        del x[rm_cmd.content.lower()]
        with open("custom_responses.json", "w") as f:
            json.dump(x, f)
        await ctx.send(f"The command '{rm_cmd.content}' has been removed.")
    else:
        await ctx.send(f"The command '{rm_cmd.content}' was not found.")
@remove_cmd.error
async def remove_cmd_error(ctx, error):
    if isinstance(error, CheckFailure):
        await ctx.send("You don't have the permissions to do that")

@client.command()
async def help(ctx):
    embed = discord.Embed(title="Bot Commands", description="Here are the available commands:", color=0x00ff00)
    
    embed.add_field(name="!cmd_list", value="List all the available questions.", inline=False)
    embed.add_field(name="!help", value="Get a list of available commands.", inline=False)
    embed.add_field(name="!banlist", value="Get a list of banned words.", inline=False)
    embed.add_field(name="!modhelp", value="Mod commands(MOD ONLY!).", inline=False)
    embed.add_field(name="!get_count", value="Get the current count number in counting channel", inline=False)
    embed.add_field(name="!profile", value="Get your or some other user's profile info. Mention the other user to get his info", inline=False)
    await ctx.send(embed=embed)
@client.command()
@has_any_role("Debugger","Admin")
async def modhelp(ctx):
    embed = discord.Embed(title="Mod Commands", description="Here are the mod commands:", color=0x00ff00)
    embed.add_field(name="!add [command] [response]", value="Add a custom command-response pair.", inline=False)
    embed.add_field(name="!addban", value="Add a custom banned word.", inline=False)
    embed.add_field(name="!removeban", value="Remove a custom banned word.", inline=False)
    
    embed.add_field(name="!remove_cmd", value="Remove a custom command-response pair.", inline=False)
    await ctx.send(embed=embed)
@modhelp.error
async def modhelp_error(ctx, error):
    if isinstance(error, CheckFailure):
        await ctx.send("You don't have the permissions to do that")
#counting
@client.command()
async def banlist(ctx):
    banned_words = "\n".join(b["banned words"])
    
    embed = discord.Embed(title="List of banned words", description=banned_words, color=0x00ff00)
    await ctx.send(embed=embed)

@client.command()
@has_any_role("Debugger","Admin")
async def addban(ctx):
    await ctx.send("Enter the word to be banned:")
    b_word = await client.wait_for('message', check=lambda m: m.author == ctx.author)

    b["banned words"].append(b_word.content)

    with open("banned_words.json", "w") as d:
        json.dump(b, d, indent=2)
    await ctx.send("added")
@addban.error
async def addban_error(ctx, error):
    if isinstance(error, CheckFailure):
        await ctx.send("You don't have the permissions to do that")


@client.command()
@has_any_role("Debugger","Admin")


async def removeban(ctx):
    await ctx.send("Enter the word to be unbanned:")
    b_word = await client.wait_for('message', check=lambda m: m.author == ctx.author)

    b["banned words"].remove(b_word.content)

    with open("banned_words.json", "w") as d:
        json.dump(b, d, indent=2)
    await ctx.send("removed")
@removeban.error
async def removeban_error(ctx, error):
    if isinstance(error, CheckFailure):
        await ctx.send("You don't have the permissions to do that")


#count

@client.command()
async def get_count(ctx):
    if ctx.channel.id != c["count_channel"]:
        ch = client.get_channel(c["count_channel"])
        await ctx.channel.send(f"This command can only run in {ch.mention}")    
    else:
        cc = c["current_count"]
        await ctx.channel.send(f"The current count is {cc}")
@client.command(name="profile")
async def profile(ctx, user: Member = None):

    if user == None:
        user = ctx.message.author

    inline = True
    embed = discord.Embed(title=user.name + "#" + user.discriminator,
                          color=discord.Color.green())
    userData = {
        "Mention": user.mention,
        "Nick": user.nick,
        "Created at": user.created_at.strftime("%b %d, %Y, %T"),
        "Joined at": user.joined_at.strftime("%b %d, %Y, %T"),
        "Server": user.guild,
        "Top role": user.top_role,
    }
    for [fieldName, fieldVal] in userData.items():
        embed.add_field(name=fieldName + ":", value=fieldVal, inline=inline)
    embed.set_footer(text=f'id: {user.id}')
    userAvatar = user.display_avatar
    embed.set_thumbnail(url=userAvatar.url)
    await ctx.send(embed=embed)



TOKEN = token1.token1
client.run(TOKEN)