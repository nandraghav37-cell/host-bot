import discord
from discord.ext import commands
import os
import re
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
OWNER_ID = int(os.getenv('OWNER_ID', '0'))  # Add your Discord ID in .env

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Allowed channels for commands
ALLOWED_CHANNELS = ['bot-chat', 'emperor-ship']  # Channel names (lowercase)

# Banned words (profanity filter)
BANNED_WORDS = ['fuck', 'shit', 'asshole', 'bastard']

# URL pattern regex
URL_PATTERN = re.compile(r'https?://|www\.|\.com|\.io|\.net|\.org|\.co')

# Warn system
warn_system = {}

def is_allowed_channel(channel):
    """Check if message is in allowed channels"""
    return channel.name.lower() in ALLOWED_CHANNELS

def is_owner(ctx):
    """Check if user is the bot owner"""
    return ctx.author.id == OWNER_ID

@bot.event
async def on_ready():
    print(f'✅ Bot logged in as {bot.user}')
    print(f'🎮 Bot is ready to moderate!')
    print(f'👑 Owner ID: {OWNER_ID}')

@bot.event
async def on_message(message):
    # Ignore bot messages
    if message.author.bot:
        return
    
    # Check for banned words (auto-timeout)
    message_lower = message.content.lower()
    for word in BANNED_WORDS:
        if word in message_lower:
            try:
                # Give 1 minute timeout
                await message.author.timeout(timedelta(minutes=1), reason=f"Abusive language: {word}")
                await message.channel.send(f"⏱️ {message.author.mention} has been timed out for 1 minute due to abusive language!")
                print(f"⏱️ {message.author} timed out for abusive language")
            except Exception as e:
                await message.channel.send(f"❌ Error: {e}")
            return
    
    # Check for links (delete + warn)
    if URL_PATTERN.search(message_lower):
        try:
            await message.delete()
            
            # Add warn
            user_id = message.author.id
            if user_id not in warn_system:
                warn_system[user_id] = 0
            warn_system[user_id] += 1
            
            warns = warn_system[user_id]
            await message.channel.send(f"🚫 {message.author.mention} - Links not allowed! **Warning {warns}/3**")
            print(f"🚫 Link deleted from {message.author} - Warning {warns}/3")
            
            # Auto-kick after 3 warnings
            if warns >= 3:
                try:
                    await message.author.kick(reason="3 link warnings")
                    await message.channel.send(f"👢 {message.author.mention} has been kicked for excessive link sharing!")
                except:
                    await message.channel.send(f"❌ Could not kick {message.author.mention}")
                warn_system[user_id] = 0
        except Exception as e:
            print(f"Error: {e}")
        return
    
    # Process commands
    await bot.process_commands(message)

# ============ GAME COMMANDS ============

@bot.command(name='ping', help='Check bot latency')
async def ping(ctx):
    if not is_allowed_channel(ctx.channel):
        return
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! {latency}ms")

@bot.command(name='hello', help='Greet the user')
async def hello(ctx):
    if not is_allowed_channel(ctx.channel):
        return
    await ctx.send(f"👋 Hello {ctx.author.mention}! Welcome to the server!")

@bot.command(name='roll', help='Roll a dice (1-6)')
async def roll(ctx):
    if not is_allowed_channel(ctx.channel):
        return
    import random
    result = random.randint(1, 6)
    await ctx.send(f"🎲 {ctx.author.mention} rolled a **{result}**!")

@bot.command(name='rps', help='Play Rock-Paper-Scissors (rock/paper/scissors)')
async def rps(ctx, choice):
    if not is_allowed_channel(ctx.channel):
        return
    import random
    
    choices = ['rock', 'paper', 'scissors']
    bot_choice = random.choice(choices)
    user_choice = choice.lower()
    
    if user_choice not in choices:
        await ctx.send("❌ Invalid choice! Use: rock, paper, or scissors")
        return
    
    # Determine winner
    if user_choice == bot_choice:
        result = "🤝 It's a tie!"
    elif (user_choice == 'rock' and bot_choice == 'scissors') or \
         (user_choice == 'paper' and bot_choice == 'rock') or \
         (user_choice == 'scissors' and bot_choice == 'paper'):
        result = f"🎉 You won! ({user_choice} vs {bot_choice})"
    else:
        result = f"😔 You lost! ({user_choice} vs {bot_choice})"
    
    await ctx.send(f"✂️ {ctx.author.mention} {result}")

@bot.command(name='guess', help='Guess a number (1-10)')
async def guess(ctx):
    if not is_allowed_channel(ctx.channel):
        return
    import random
    
    secret = random.randint(1, 10)
    await ctx.send(f"🎯 {ctx.author.mention} I'm thinking of a number 1-10. You have 3 tries!")
    
    tries = 0
    while tries < 3:
        try:
            msg = await bot.wait_for('message', timeout=30, check=lambda m: m.author == ctx.author)
            try:
                guess_num = int(msg.content)
                if guess_num == secret:
                    await ctx.send(f"🎉 Correct! The number was **{secret}**!")
                    return
                elif guess_num < secret:
                    await ctx.send(f"📈 Higher!")
                else:
                    await ctx.send(f"📉 Lower!")
                tries += 1
            except:
                await ctx.send("❌ Enter a valid number!")
        except:
            await ctx.send(f"⏱️ Time's up! The number was **{secret}**")
            return

# ============ MODERATION COMMANDS (OWNER ONLY) ============

@bot.command(name='timeout', help='Timeout a user (!timeout @user [minutes]) - OWNER ONLY')
@commands.check(is_owner)
async def timeout(ctx, member: discord.Member, minutes: int = 1):
    if not is_allowed_channel(ctx.channel):
        return
    
    try:
        await member.timeout(timedelta(minutes=minutes), reason=f"Timeout by {ctx.author}")
        await ctx.send(f"⏱️ {member.mention} has been timed out for {minutes} minute(s)!")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

@bot.command(name='ban', help='Ban a user (!ban @user [reason]) - OWNER ONLY')
@commands.check(is_owner)
async def ban(ctx, member: discord.Member, *, reason="No reason"):
    if not is_allowed_channel(ctx.channel):
        return
    
    try:
        await member.ban(reason=reason)
        await ctx.send(f"🔨 {member.mention} has been banned! Reason: {reason}")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

@bot.command(name='kick', help='Kick a user (!kick @user [reason]) - OWNER ONLY')
@commands.check(is_owner)
async def kick(ctx, member: discord.Member, *, reason="No reason"):
    if not is_allowed_channel(ctx.channel):
        return
    
    try:
        await member.kick(reason=reason)
        await ctx.send(f"👢 {member.mention} has been kicked! Reason: {reason}")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

@bot.command(name='mute', help='Mute a user - OWNER ONLY')
@commands.check(is_owner)
async def mute(ctx, member: discord.Member):
    if not is_allowed_channel(ctx.channel):
        return
    
    try:
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not mute_role:
            mute_role = await ctx.guild.create_role(name="Muted")
        
        await member.add_roles(mute_role)
        await ctx.send(f"🔇 {member.mention} has been muted!")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

@bot.command(name='unmute', help='Unmute a user - OWNER ONLY')
@commands.check(is_owner)
async def unmute(ctx, member: discord.Member):
    if not is_allowed_channel(ctx.channel):
        return
    
    try:
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if mute_role:
            await member.remove_roles(mute_role)
            await ctx.send(f"🔊 {member.mention} has been unmuted!")
        else:
            await ctx.send("❌ Muted role not found!")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

@bot.command(name='warn', help='Warn a user (!warn @user [reason]) - OWNER ONLY')
@commands.check(is_owner)
async def warn(ctx, member: discord.Member, *, reason="No reason"):
    if not is_allowed_channel(ctx.channel):
        return
    
    user_id = member.id
    if user_id not in warn_system:
        warn_system[user_id] = 0
    
    warn_system[user_id] += 1
    warns = warn_system[user_id]
    
    await ctx.send(f"⚠️ {member.mention} warned! Reason: {reason}\n**Warning {warns}/3**")
    
    if warns >= 3:
        try:
            await member.kick(reason="3 warnings")
            await ctx.send(f"👢 {member.mention} has been kicked for excessive warnings!")
        except:
            await ctx.send(f"❌ Could not kick {member.mention}")
        warn_system[user_id] = 0

# Error handler for permission check
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send(f"❌ Only the bot owner can use this command! 👑")

@bot.command(name='myhelp', help='Show all commands')
async def myhelp(ctx):
    if not is_allowed_channel(ctx.channel):
        return
    
    embed = discord.Embed(title="🤖 Bot Commands", color=discord.Color.blue())
    
    embed.add_field(name="🎮 Games (Everyone)", value=
        "• `!ping` - Check latency\n"
        "• `!hello` - Say hello\n"
        "• `!roll` - Roll a dice\n"
        "• `!rps rock/paper/scissors` - Rock-Paper-Scissors\n"
        "• `!guess` - Number guessing game", inline=False)
    
    embed.add_field(name="🛡️ Moderation (OWNER ONLY 👑)", value=
        "• `!timeout @user [minutes]` - Timeout user\n"
        "• `!ban @user [reason]` - Ban user\n"
        "• `!kick @user [reason]` - Kick user\n"
        "• `!mute @user` - Mute user\n"
        "• `!unmute @user` - Unmute user\n"
        "• `!warn @user [reason]` - Warn user", inline=False)
    
    embed.add_field(name="🚫 Auto-Moderation (Automatic)", value=
        "• ⏱️ Abusive words = 1 min timeout\n"
        "• 🚫 Links = Delete + Warning\n"
        "• 3 warnings = Auto kick", inline=False)
    
    embed.add_field(name="📍 Allowed Channels", value="• #bot-chat\n• #👑emperor-ship-❤️‍🔥", inline=False)
    
    await ctx.send(embed=embed)

# Run bot
bot.run(TOKEN)
