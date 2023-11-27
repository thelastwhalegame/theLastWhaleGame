import discord
from discord.ext import commands
import sqlite3
from configProd import BOT_TOKEN

intents = discord.Intents.default()
intents.message_content = True
intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Канал, куда будут отправляться никнеймы
output_channel_id = 1176447684824023161  # Замените на ID вашего канала

# Имя файла базы данных SQLite
db_filename = 'airdrop_testers.db'

# Создание таблицы в базе данных
def create_table():
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processed_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER
        );
    ''')
    conn.commit()
    conn.close()


# Проверка наличия пользователя в базе данных
def is_user_processed(user_id):
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM processed_users WHERE user_id = ?;', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return bool(result)


# Добавление пользователя в базу данных
def add_processed_user(user_id):
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO processed_users (user_id) VALUES (?);', (user_id,))
    conn.commit()
    conn.close()


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')
    create_table()


@bot.command(name='want_to_test')
async def want_to_test(ctx):
    # Проверяем, был ли пользователь уже обработан
    if not is_user_processed(ctx.author.id):
        # Отправляем никнейм пользователя в указанный канал
        channel = bot.get_channel(output_channel_id)
        if channel:
            await channel.send(f"User {ctx.author.name} wants to test!")

        # Добавляем пользователя в базу данных, чтобы избежать дубликатов
        add_processed_user(ctx.author.id)
    else:
        await ctx.send(f"{ctx.author.mention}, you have already been processed before.")


# Запуск бота
bot.run(BOT_TOKEN)