# Discord Bot 🤖

A fun Discord bot with games and commands for chat purposes.

## Features
- ✅ **Rock-Paper-Scissors game** - `!rps rock|paper|scissors`
- ✅ **Number guessing game** - `!guess [1-10]`
- ✅ **Dice roller** - `!roll`
- ✅ **Custom commands** - `!ping`, `!hello`, `!help`

## Setup

### 1. Create Discord Bot Token
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Go to "Bot" tab and click "Add Bot"
4. Copy the token
5. Create a `.env` file and add:
   ```
   DISCORD_TOKEN=your_token_here
   ```

### 2. Invite Bot to Server
1. Go to OAuth2 → URL Generator
2. Select scopes: `bot`
3. Select permissions: `Send Messages`, `Read Messages`
4. Copy the generated URL and open it in browser

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Bot
```bash
python main.py
```

## Commands

| Command | Description |
|---------|-------------|
| `!ping` | Check bot latency |
| `!hello` | Say hello |
| `!roll` | Roll a dice (1-6) |
| `!rps [rock/paper/scissors]` | Play Rock-Paper-Scissors |
| `!guess [1-10]` | Guess a number |
| `!help` | Show all commands |

## Deployment on Railway

1. Push code to GitHub
2. Connect GitHub repo to Railway
3. Add `DISCORD_TOKEN` environment variable in Railway
4. Deploy!

## Add More Commands

Edit `main.py` and add new commands:
```python
@bot.command(name='yourcommand', help='Description')
async def your_command(ctx):
    await ctx.send('Response here')
```

Then restart the bot!
