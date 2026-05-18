const { Client, Events, GatewayIntentBits, Partials, ChannelType } = require("discord.js");

const ALLOWED_CHANNEL_KEYWORDS = ["📍", "👑"];
const WELCOME_CHANNEL_KEYWORD = "📍";

const GENZ_REPLIES = [
  "fr fr no cap 💀", "bro that's wild ngl", "lowkey same bro", "W take honestly",
  "ngl that's kinda based", "bruh 💀💀", "slay fr", "it's giving vibes ngl",
  "bro really said that 💀", "not me agreeing with this", "okay but fr though",
  "that's so real bro", "nah bro that's an L", "W bro W", "no cap that slaps",
  "bro is cooked 💀", "lowkey a banger take", "it's giving main character energy",
  "sheesh bro said it", "ngl kinda bussin", "bro woke up and chose chaos",
  "okay bestie we hear you", "not the drama 💀", "based and real",
  "understood the assignment bro", "that's sending me 💀",
];

const GREET_REPLIES = [
  "heyyy what's good 👋", "ayo what's up bro", "heyy fr fr", "wassup bestie", "ayo gang 👑",
];

const BOT_REPLIES = [
  "nah bro can't help with that 💀", "not my department bro", "lowkey no clue bro",
];

function getRandom(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function getReply(message) {
  const lower = message.toLowerCase();
  if (lower.includes("bot") || lower.includes("host")) return getRandom(BOT_REPLIES);
  if (["hi", "hey", "hello", "hii", "heyy", "sup", "yo", "ayo"].some(w => lower.startsWith(w) || lower === w)) {
    return getRandom(GREET_REPLIES);
  }
  return getRandom(GENZ_REPLIES);
}

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.GuildMembers,
    GatewayIntentBits.MessageContent,
    GatewayIntentBits.DirectMessages,
  ],
  partials: [Partials.Channel, Partials.Message],
});

client.once(Events.ClientReady, (c) => {
  console.log(`Bot ready! Logged in as ${c.user.tag}`);
});

client.on(Events.GuildMemberAdd, async (member) => {
  try {
    const welcomeChannel = member.guild.channels.cache.find(
      (ch) => ch.type === ChannelType.GuildText && ch.name.includes(WELCOME_CHANNEL_KEYWORD)
    );
    if (welcomeChannel && welcomeChannel.type === ChannelType.GuildText) {
      await welcomeChannel.send(`👑 Welcome to the server, <@${member.id}>! Glad to have you here. Feel free to chat!`);
    }
  } catch (err) {
    console.error("Error sending welcome message:", err);
  }
});

client.on(Events.MessageCreate, async (message) => {
  if (message.author.bot) return;

  if (
    message.channel.type === ChannelType.GuildText &&
    !ALLOWED_CHANNEL_KEYWORDS.some((kw) =>
      message.channel.type === ChannelType.GuildText && message.channel.name.includes(kw)
    )
  ) return;

  if (message.reference && message.mentions.repliedUser?.id !== client.user?.id) return;

  const mentionedOtherUser = message.mentions.users.some((u) => u.id !== client.user?.id);
  if (mentionedOtherUser) return;

  const content = message.content.replace(/<@!?[\d]+>/g, "").trim();
  if (!content) return;

  try {
    await message.channel.sendTyping();
    await message.reply(getReply(content));
  } catch (err) {
    console.error("Error sending reply:", err);
  }
});

client.login(process.env.DISCORD_TOKEN).catch((err) => {
  console.error("Failed to login:", err);
  process.exit(1);
});
