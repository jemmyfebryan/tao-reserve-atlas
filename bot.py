"""
Atlas - TaoReserve Discord Bot
An AI-powered Discord bot that answers questions about Bittensor using RAG.
"""

import discord
import os
import sys
from dotenv import load_dotenv
from agent import BittensorAgent

# Force flush output
sys.stdout.reconfigure(line_buffering=True)

# Load environment variables
load_dotenv()
print("✓ Environment loaded", flush=True)

# Configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
TARGET_CHANNEL_ID = os.getenv('TARGET_CHANNEL_ID')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Validate configuration with helpful error messages
errors = []

if not DISCORD_TOKEN:
    errors.append("❌ DISCORD_TOKEN is missing in .env file")

if not TARGET_CHANNEL_ID:
    errors.append("❌ TARGET_CHANNEL_ID is missing in .env file")
else:
    try:
        TARGET_CHANNEL_ID = int(TARGET_CHANNEL_ID)
    except ValueError:
        errors.append("❌ TARGET_CHANNEL_ID must be a valid number")

if not GEMINI_API_KEY:
    errors.append("❌ GEMINI_API_KEY is missing in .env file")

if errors:
    print("\n" + "="*70, flush=True)
    print("❌ Configuration Error - Atlas Bot Cannot Start", flush=True)
    print("="*70, flush=True)
    for error in errors:
        print(error, flush=True)
    print("\n" + "="*70, flush=True)
    print("Please fix your .env file:", flush=True)
    print("  cp .env.example .env", flush=True)
    print("  # Edit .env and add your API keys", flush=True)
    print("="*70 + "\n", flush=True)
    sys.exit(1)

# Set up Discord intents
intents = discord.Intents.default()
intents.message_content = True

# Initialize the AI agent
print("✓ Initializing AI agent...", flush=True)
agent = BittensorAgent(model="models/gemini-2.5-flash")
print("✓ AI agent ready", flush=True)

# Set up Discord client
client = discord.Client(intents=intents)
print("✓ Discord client initialized", flush=True)


@client.event
async def on_ready():
    """Called when the bot is ready."""
    print(f'\n{'='*70}', flush=True)
    print(f'✓ Atlas Bot Online!', flush=True)
    print(f'{'='*70}', flush=True)
    print(f'Bot: {client.user} (ID: {client.user.id})', flush=True)
    print(f'Server: Tao Reserve', flush=True)
    print(f'Channel ID: {TARGET_CHANNEL_ID}', flush=True)
    print(f'Mission: Connect subnet owners with developers', flush=True)
    print(f'{'='*70}\n', flush=True)


@client.event
async def on_message(message):
    """
    Handle incoming messages.
    Use AI agent to answer questions about Bittensor.
    """
    # 1. Ignore messages from bots
    if message.author.bot:
        return

    # 2. Only respond in the specific channel
    if message.channel.id != TARGET_CHANNEL_ID:
        return

    # 3. Show "typing..." while processing
    async with message.channel.typing():
        try:
            # Get the question from user's message
            question = message.content.strip()

            print(f'\n{'='*70}')
            print(f'[{message.author}] {question}')
            print(f'{'='*70}')

            # Get answer from AI agent
            answer = agent.query_simple(question)

            print(f'Answer: {answer[:100]}...')
            print(f'{'='*70}\n')

            # Discord has a 2000 character limit per message
            if len(answer) > 2000:
                # Split long messages
                chunks = [answer[i:i+1997] for i in range(0, len(answer), 1997)]
                for i, chunk in enumerate(chunks, 1):
                    if i == len(chunks):
                        await message.reply(chunk)
                    else:
                        await message.reply(chunk)
                    import asyncio
                    await asyncio.sleep(0.5)  # Small delay between chunks
            else:
                await message.reply(answer)

        except Exception as e:
            print(f'Error processing message: {e}')
            import traceback
            traceback.print_exc()
            await message.reply(
                "Sorry, I encountered an error while processing your question. "
                "Please try again or contact support if the issue persists."
            )


# Start the bot
print("✓ Bot initialization complete", flush=True)

def start_bot():
    """Start the Discord bot."""
    print('\n' + '='*70, flush=True)
    print('🤖 Starting Atlas Bot...', flush=True)
    print('='*70 + '\n', flush=True)

    try:
        print("✓ Connecting to Discord...", flush=True)
        client.run(DISCORD_TOKEN)
    except Exception as e:
        print(f"\n{'='*70}", flush=True)
        print(f"❌ Fatal Error: {e}", flush=True)
        print(f"{'='*70}\n", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    start_bot()
