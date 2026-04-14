"""
Atlas - TaoReserve Discord Bot
An AI-powered Discord bot that answers questions about Bittensor using RAG.
"""

import discord
import os
from dotenv import load_dotenv
from agent import BittensorAgent

# Load environment variables
load_dotenv()

# Configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
TARGET_CHANNEL_ID = int(os.getenv('TARGET_CHANNEL_ID', 0))
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Validate configuration
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN is required. Set it in .env file")
if not TARGET_CHANNEL_ID:
    raise ValueError("TARGET_CHANNEL_ID is required. Set it in .env file")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is required. Set it in .env file")

# Set up Discord intents
intents = discord.Intents.default()
intents.message_content = True

# Initialize the AI agent
agent = BittensorAgent(model="models/gemini-2.5-flash")

# Set up Discord client
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    """Called when the bot is ready."""
    print(f'{'='*70}')
    print(f'✓ Atlas Bot Online!')
    print(f'{'='*70}')
    print(f'Logged in as: {client.user} (ID: {client.user.id})')
    print(f'Listening to Channel ID: {TARGET_CHANNEL_ID}')
    print(f'Using Gemini AI for intelligent responses')
    print(f'{'='*70}\n')


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
if __name__ == "__main__":
    print('\n🤖 Starting Atlas Bot...')
    client.run(DISCORD_TOKEN)
