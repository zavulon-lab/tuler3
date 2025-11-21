from bot import bot
from discord.ui import View
from constructor import (  
    FormModal, 
    VerificationRequestModal, 
    PersonalChannelModal,
    MainChannelButtons,
    ApplicationChannelButtons,
    VerificationRequestButtons,
    PersonalChannelButtons
)
from json_func import channels
from discord import Interaction, Object, app_commands, TextChannel, Embed
from datetime import datetime
import discord

GUILD_ID = 1421879715081224304  # ID сервера

APPLICATION_CHANNEL_ID = 1441477056620662904  # ID канала для заявок 


CATEGORY_ID = 1425985017125011587 # ID категории для заявок и приватных каналов
 
MAIN_CHANNEL_ID = 1441478266048352256  # ID основного канала  
ROLE_ID = 1422645151037264003  # ID роли для доступа к заявкам
PRIVATE_CHANNEL_ID = 1441478550212448348  # ID канала для приватных каналов
PRIVATE_THREAD_ROLE_ID = 1422645151037264003  # ID роли для доступа к приватным каналам
ALLOWED_ROLE_ID = 1422645151037264003  # ID роли для создания каналов
VERIFICATION_REQUEST_CHANNEL_ID = 1425194688926715996  # ID канала для подачи запросов на проверку
VERIFICATION_ADMIN_CHANNEL_ID = 1425194883102019716  # ID канала для админских действий
VERIFICATION_NOTIFICATION_CHANNEL_ID = 1425195260665135267  # ID канала для уведомлений о проверке
VOICE_CHANNEL_ID = 1441478939661963276  # ID голосового канала для проверок
PERSONAL_CHANNEL_REQUEST_ID = 1425577110331985930
LOG_CHANNEL_ID = 1441479124311871599  #  канал для логов заявок
PERSONAL_CATEGORY_ID = 1441477900439130283
HUNTER_ROLE_ID = 1426134099478970499

ACADEMY_CHANNEL_ID = 1437897167032549437
CURATOR_ROLE_ID = 1437905190198968381  # Роль кураторов

CAPT_ARCHIVE_ID = 1441479958844407901  # канал "Капт-архив"
MCL_ARCHIVE_ID  = 1441479923071189072   # канал "Мкл-архив"




def has_allowed_role(interaction: Interaction) -> bool:
    return any(role.id == ALLOWED_ROLE_ID for role in interaction.user.roles)


# ========== ЕДИНСТВЕННЫЙ on_ready ВО ВСЁМ ПРОЕКТЕ ==========
@bot.event
async def on_ready():
    print(f"Бот {bot.user} запущен!")
    await bot.tree.sync(guild=Object(id=GUILD_ID))
    print("Команды синхронизированы!")

    CHANNELS = [
        (MAIN_CHANNEL_ID, "Отправка отката", "", MainChannelButtons),
        (APPLICATION_CHANNEL_ID, "Подача заявки", "", ApplicationChannelButtons),
        (VERIFICATION_REQUEST_CHANNEL_ID, "Запрос на проверку", "", VerificationRequestButtons),
        (PERSONAL_CHANNEL_REQUEST_ID, "Создание личного дела", "", PersonalChannelButtons),
    ]

    try:
        for CHANNEL_ID, title, button_text, ButtonClass in CHANNELS:
            channel = bot.get_channel(CHANNEL_ID)
            if not channel:
                print(f"Канал {CHANNEL_ID} не найден!")
                continue

            await channel.purge(limit=100)

            if CHANNEL_ID == MAIN_CHANNEL_ID:
                embed = discord.Embed(
                    title="🎥 Отправка откатов",
                    description=(
                        "После мероприятия хайранги создают канал\n"
                        "для хранения и анализа откатов с мероприятия\n\n"
                        "Выбирай канал ниже и прикрепляй видео/скриншоты.\n\n"
                        "Требования к откату:\n"
                        "• ✦ Полная запись мероприятия без монтажа\n"
                        "• ✦ Загруженная на YouTube или RuTube\n"
                        "• ✦ Откаты автоматически дублируются в ваше личное дело 📂"
                    ),
                    color=0x000000
                )
                embed.set_thumbnail(url="https://media.discordapp.net/attachments/1426830745573392435/1427004851715309588/tuleshkin_logoNEW2.jpg")
                embed.set_footer(text="Tuleshkin Majestic")

            elif CHANNEL_ID == APPLICATION_CHANNEL_ID:
                embed = discord.Embed(
                    title="✦ TULESHKIN famq",
                    description=(
                        "📞 Приглашение на обзвон приходит в отдельном канале\n"
                        "⏳ Рассмотрение заявки: от 1 до 2 дней\n"
                    ),
                    color=0x000000
                )
                embed.set_thumbnail(url="https://media.discordapp.net/attachments/1426830745573392435/1427004851715309588/tuleshkin_logoNEW2.jpg")
                embed.add_field(
                    name="⚡ Обязательные требования",
                    value=(
                        "• 16+ лет\n"
                        "• Онлайн от 4+ часов в день\n"
                        "• Отсутствие токсичности"
                    ),
                    inline=False
                )
                embed.set_footer(text="Tuleshkin Majestic | Разработчик — viral")

            elif CHANNEL_ID == VERIFICATION_REQUEST_CHANNEL_ID:
                embed = discord.Embed(
                    title="🔍 Запрос на проверку",
                    description=(
                        "Чтобы играть мп в огране в нашей семье — нужна проверка\n\n"
                        "Нажми кнопку ниже и оставь запрос\n"
                        "⚡ Мы ответим в ближайшее время\n"
                    ),
                    color=0x000000
                )
                embed.set_thumbnail(url="https://media.discordapp.net/attachments/1426830745573392435/1427004851715309588/tuleshkin_logoNEW2.jpg")
                embed.set_footer(text="Tuleshkin Majestic")

            elif CHANNEL_ID == PERSONAL_CHANNEL_REQUEST_ID:
                embed = discord.Embed(
                    title="📂 Отправить в личное дело",
                    description="✨ Нажми кнопку ниже и отправь откат или ссылку — всё сохранится автоматически",
                    color=0x000000
                )
                embed.set_footer(text="Tuleshkin Majestic")


            else:
                embed = discord.Embed(title=title, color=0x3A3B3C)
                embed.set_footer(text="Tuleshkin Majestic")

            embed.timestamp = datetime.now()
            await channel.send(embed=embed)
            await channel.send(view=ButtonClass())

            print(f"Опубликовано в #{channel.name}")

            

    except Exception as e:
        print(f"Ошибка в on_ready: {e}")
# ========== КОМАНДЫ ==========




@bot.event
async def on_channel_delete(channel: TextChannel):
    if channel.id in channels:
        del channels[channel.id]


@bot.tree.command(name="заявка1", description="Заполнить заявку", guild=Object(id=GUILD_ID))
async def application(interaction: Interaction):
    await interaction.response.send_modal(FormModal())


@bot.tree.command(name="запрос_на_проверку", description="Запрос на проверку", guild=Object(id=GUILD_ID))
async def verification_request(interaction: Interaction):
    await interaction.response.send_modal(VerificationRequestModal())


@bot.tree.command(name="личное_дело", description="Создать личное дело", guild=Object(id=GUILD_ID))
async def personal_channel(interaction: Interaction):
    await interaction.response.send_modal(PersonalChannelModal())


@bot.tree.command(name="sync", description="Синх команд", guild=Object(id=GUILD_ID))
async def sync(interaction: Interaction):
    await bot.tree.sync(guild=Object(id=GUILD_ID))
    await interaction.response.send_message("Команды синхронизированы!", ephemeral=True)
