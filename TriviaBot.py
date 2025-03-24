import sqlite3
import discord
from discord.ext import commands, tasks
import requests

current_question = ""
current_answer = ""

def pull_question():
    url = "https://opentdb.com/api.php?amount=1&category=17&type=multiple"
    data = requests.get(url).json()
    question_data = data["results"][0]
    return question_data["question"], question_data["correct_answer"]


conn = sqlite3.connect("trivia.db")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS scores (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        score INTEGER DEFAULT 0
    )
''')

conn.commit()
conn.close()

TOKEN = "input_token"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    update_trivia_question.start()

    channel = bot.get_channel(1343798433223413865)

    if channel:
        await channel.send("Hello, I am Trivia Bot. (type !options to access the menu)")

@bot.event
async def on_message(message):
    print(f"Message received: {message.content}")
    await bot.process_commands(message)

@tasks.loop(minutes=5)
async def update_trivia_question():
    global current_question, current_answer
    question, answer = pull_question()
    current_question = question
    current_answer = answer
    print(f"New Question: {current_question} - Answer: {current_answer}")

@bot.command()
async def options(ctx):
    help_message = """
    What do you need help with?
    
    a. Info
    b. Trivia
    c. Scores
    d. Other

    Please type the option you need help with (!info, !trivia, !scores, !other)
    """
    await ctx.send(help_message)

@bot.command()
async def info(ctx):
    info_message = """
    Trivia Bot from Group 17 is easily the best bot ever.
    We are be developing trivia administration technologies that will
    bring any discord server to life with a thriving trivia ecosystem.
    
    Group 17 Rules!
    """
    await ctx.send(info_message)

@bot.command()
async def trivia(ctx):
    trivia_commands = """
    Trivia game commands.
    
    !join_game - Varify that you are on the scoreboard
    !question - See the current question (updates every five minutes)
    !answer - Submit answer using the format (!answer "your answer")
    """
    await ctx.send(trivia_commands)

@bot.command()
async def scores(ctx):
    conn = sqlite3.connect("trivia.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username, score FROM scores ORDER BY score DESC")
    scores = cursor.fetchall()
    conn.close()

    score_message = "Top Scores:\n"
    for i, (username, score) in enumerate(scores, 1):
        score_message += f"{i}. {username} - {score} points\n"

    await ctx.send(score_message)

@bot.command()
async def other(ctx):
    username = ctx.author.name
    await ctx.send(f"Hello {username}, please message the server moderator for further assistance.")

@bot.command()
async def question(ctx):
    await ctx.send(f"Current Question: {current_question}")

@bot.command()
async def join_game(ctx):
    user_id = ctx.author.id
    username = ctx.author.name

    conn = sqlite3.connect("trivia.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM scores WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    if result:
        await ctx.send(f"Welcome Back {username}")
    else:
        cursor.execute("INSERT INTO scores (user_id, username, score) VALUES (?, ?, ?)", (user_id, username, 0))
        conn.commit()
        await ctx.send(f"Welcome {username}!")

    conn.close()


@bot.command()
async def answer(ctx, *, user_answer: str):
    user_id = ctx.author.id
    username = ctx.author.name

    user_answer = user_answer.strip().lower()
    correct_answer = current_answer.strip().lower()

    if user_answer == correct_answer:
        conn = sqlite3.connect("trivia.db")
        cursor = conn.cursor()

        cursor.execute("SELECT score FROM scores WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()

        if result:
            new_score = result[0] + 1
            cursor.execute("UPDATE scores SET score = ? WHERE user_id = ?", (new_score, user_id))
            conn.commit()
            await ctx.send(f"Correct! {username} - {new_score} points.")
        else:
            await ctx.send(
                "No score found, please !join_game.")

        conn.close()
    else:
        await ctx.send(f"Sorry {username}, Try again!")


bot.run(TOKEN)