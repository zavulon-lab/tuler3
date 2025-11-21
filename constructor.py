# constructor.py — ИМПОРТЫ (идеальные, без дубликатов)
from json_func import private_channels, save_private_channels, save_all, add_private_channel
from datetime import datetime
from discord import Thread
import asyncio

import discord
from discord import (
    Interaction,
    CategoryChannel,
    TextChannel,
    SelectOption,
    TextStyle,
    ButtonStyle,
    Embed
)
from discord.ui import View, Select, Modal, TextInput, button, Button
from discord.errors import HTTPException, NotFound

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
VOICE_CHANNEL_ID = 1422641907607277773  # ID голосового канала для проверок
PERSONAL_CHANNEL_REQUEST_ID = 1425577110331985930
LOG_CHANNEL_ID = 1441479124311871599  #  канал для логов заявок
PERSONAL_CATEGORY_ID = 1441477900439130283
HUNTER_ROLE_ID = 1426134099478970499

ACADEMY_CHANNEL_ID = 1437897167032549437
CURATOR_ROLE_ID = 1437905190198968381  # Роль кураторов

CAPT_ARCHIVE_ID = 1441479958844407901  # канал "Капт-архив"
MCL_ARCHIVE_ID  = 1441479923071189072   # канал "Мкл-архив"


# -------------------------
# Вспомогательные утилиты
# -------------------------
async def safe_respond(interaction: Interaction, content: str, ephemeral: bool = True):
    """
    Безопасно отвечаем на интеракцию: если уже ответили — используем followup.
    """
    try:
        await interaction.response.send_message(content, ephemeral=ephemeral)
    except Exception:
        try:
            await interaction.followup.send(content, ephemeral=ephemeral)
        except Exception:
            # уже ничего не можем сделать
            pass

def make_base_embed(title: str, description: str = "") -> Embed:
    e = Embed(
        title=title,
        description=description or "",
        color=0x3A3B3C,
        timestamp=datetime.now()
    )
    e.set_footer(text="Настройте текст в этом embed")
    return e

# -------------------------
# МОДАЛКИ
# -------------------------

class FormModal(Modal, title="Заявка на вступление в семью"):
    name = TextInput(label="Ник в игре | Статик | Имя и возраст", required=True)
    rp_experience = TextInput(label="Все ваши предыдущие семьи", required=True, style=TextStyle.paragraph)
    shooting = TextInput(label="Откаты с гг", required=True, style=TextStyle.paragraph)
    lvl_online = TextInput(label="Цель вступления", required=True)
    family_experience = TextInput(label="Как узнали о семье", required=True, style=TextStyle.paragraph)

    async def on_submit(self, interaction: Interaction):
        try:
            guild = interaction.guild
            applicant = interaction.user

            category = guild.get_channel(PERSONAL_CATEGORY_ID)
            if not category or not isinstance(category, CategoryChannel):
                return await safe_respond(interaction, "❌ Категория личных дел не найдена.", True)

            # Безопасное имя канала
            channel_name = f"заявка-{applicant.display_name.lower().replace(' ', '-')}-{applicant.id}"[-100:]
            new_channel = await guild.create_text_channel(
                name=channel_name,
                category=category,
                reason=f"Заявка от {applicant}"
            )

            # Права доступа
            await new_channel.set_permissions(guild.default_role, view_channel=False)
            role = guild.get_role(ROLE_ID)
            if role:
                await new_channel.set_permissions(role, view_channel=True)
            await new_channel.set_permissions(applicant, view_channel=True, read_message_history=True)

            # Сбор данных заявки один раз
            app_data = {
                "name": self.name.value.strip() or "—",
                "rp_experience": self.rp_experience.value.strip() or "—",
                "shooting": self.shooting.value.strip() or "—",
                "lvl_online": self.lvl_online.value.strip() or "—",
                "family_experience": self.family_experience.value.strip() or "—",
            }

            # Красивый эмбед заявки
            embed = discord.Embed(
                title="✦ Новая заявка на вступление в семью",
                description="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nСпасибо, что решили присоединиться к нам ❤️\nАдминистрация рассмотрит вашу заявку в ближайшее время.\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                color=0x2B2D31,
                timestamp=datetime.now()
            )
            embed.add_field(name="🎫 Ник | Статик | Имя и возраст", value=f"```{app_data['name']}```", inline=False)
            embed.add_field(name="🏛 Прошлые семьи", value=f"```{app_data['rp_experience']}```", inline=False)
            embed.add_field(name="🔫 Откаты с ГГ", value=f"```{app_data['shooting']}```", inline=False)
            embed.add_field(name="🎯 Цель вступления", value=f"```{app_data['lvl_online']}```", inline=False)
            embed.add_field(name="📢 Откуда узнал о нас", value=f"```{app_data['family_experience']}```", inline=False)
            embed.add_field(name="👤 Пользователь", value=f"{applicant.mention}\nАккаунт создан: <t:{int(applicant.created_at.timestamp())}:R>", inline=True)
            embed.add_field(name="🆔 ID", value=f"```{applicant.id}```", inline=True)
            embed.set_thumbnail(url=applicant.display_avatar.url)
            embed.set_footer(text="Семья • Заявка на вступление", icon_url=guild.icon.url if guild.icon else None)

            # Кнопки + логи
            # ←←←←← ВНЕ FormModal — новый класс с параметрами ←←←←←
            class ApplicationAdminButtons(discord.ui.View):
                def __init__(self, applicant: discord.Member, application_channel: discord.TextChannel, app_data: dict):
                    super().__init__(timeout=None)
                    self.applicant = applicant
                    self.application_channel = application_channel
                    self.app_data = app_data  # словарь с данными заявки

                async def check_perm(self, inter: Interaction) -> bool:
                    if inter.user.guild_permissions.administrator:
                        return True
                    if any(r.id == ALLOWED_ROLE_ID for r in inter.user.roles):
                        return True
                    await safe_respond(inter, "❌ У тебя нет прав на работу с заявками!", ephemeral=True)
                    return False

                async def send_log(self, inter: Interaction, status: str, color: int):
                    log_channel = inter.guild.get_channel(LOG_CHANNEL_ID)
                    if not log_channel:
                        return

                    log_embed = discord.Embed(
                        title=f"Заявка {status}",
                        description=f"**Кандидат:** {self.applicant.mention}\n**Обработал:** {inter.user.mention}",
                        color=color,
                        timestamp=datetime.now()
                    )
                    log_embed.add_field(name="Ник | Статик | Имя и возраст", value=f"```{self.app_data['name']}```", inline=False)
                    log_embed.add_field(name="Прошлые семьи", value=f"```{self.app_data['rp_experience']}```", inline=False)
                    log_embed.add_field(name="Откаты с ГГ", value=f"```{self.app_data['shooting']}```", inline=False)
                    log_embed.add_field(name="Цель вступления", value=f"```{self.app_data['lvl_online']}```", inline=False)
                    log_embed.add_field(name="Откуда узнал", value=f"```{self.app_data['family_experience']}```", inline=False)
                    log_embed.add_field(name="Канал заявки", value="Удалён", inline=True)
                    log_embed.add_field(name="Обработал", value=inter.user.mention, inline=True)
                    log_embed.set_thumbnail(url=self.applicant.display_avatar.url)
                    log_embed.set_footer(text=f"ID: {self.applicant.id}")

                    await log_channel.send(embed=log_embed)

                @button(label="Принять", style=ButtonStyle.success, custom_id="app_accept_final")
                async def accept(self, inter: Interaction, button: Button):
                    if not await self.check_perm(inter):
                        return

                    try:
                        if not inter.response.is_done():
                            await inter.response.defer(ephemeral=True)
                    except:
                        pass

                    user_id_str = str(self.applicant.id)

                    # ←←←←← ГЛАВНОЕ: ПРОВЕРЯЕМ, ЕСТЬ ЛИ УЖЕ ЛИЧНОЕ ДЕЛО ←←←←←
                    if user_id_str in private_channels:
                        existing_channel = inter.guild.get_channel(private_channels[user_id_str])
                        if existing_channel:
                            await inter.followup.send(
                                f"✅ Заявка {self.applicant.mention} принята!\n"
                                f"Личное дело уже существует: {existing_channel.mention}",
                                ephemeral=False
                            )
                        else:
                            # Если канал удалён, но ID остался — пересоздаём
                            pass  # продолжаем ниже
                    else:
                        # Создаём новое личное дело
                        category = inter.guild.get_channel(CATEGORY_ID)
                        if not category:
                            return await inter.followup.send("❌ Категория личных дел не найдена!", ephemeral=True)

                        channel_name = f"{self.applicant.display_name.lower().replace(' ', '-')}"[-100:]
                        personal_channel = await inter.guild.create_text_channel(
                            name=channel_name,
                            category=category,
                            reason=f"Личное дело ({self.applicant}) — принятие заявки"
                        )

                        await personal_channel.set_permissions(inter.guild.default_role, view_channel=False)
                        await personal_channel.set_permissions(self.applicant, view_channel=True, send_messages=True, read_message_history=True)
                        await personal_channel.set_permissions(inter.user, view_channel=True, send_messages=True)

                        add_private_channel(self.applicant.id, personal_channel.id)

                        # Академия
                        academy = inter.guild.get_channel(ACADEMY_CHANNEL_ID)
                        if academy:
                            embed = discord.Embed(
                                title="Новый участник принят",
                                description=f"{self.applicant.mention} — {inter.user.mention} принял(a)\n"
                                            f"Личное дело: {personal_channel.mention}\n"
                                            f"Куратор — {inter.user.mention}",
                                color=0x00ff00,
                                timestamp=datetime.now()
                            )
                            await academy.send(embed=embed)

                    await self.send_log(inter, "УСПЕШНО ПРИНЯТА", 0x00ff00)
                    await inter.followup.send(f"✅ Заявка {self.applicant.mention} принята!", ephemeral=False)

                    for item in self.children:
                        item.disabled = True
                    await inter.message.edit(view=self)

                    await asyncio.sleep(5)
                    try:
                        await self.application_channel.delete(reason=f"Заявка принята — {inter.user}")
                    except:
                        pass

                @button(label="Отклонить", style=ButtonStyle.danger, custom_id="app_reject_final")
                async def reject(self, inter: Interaction, button: Button):
                    if not await self.check_perm(inter):
                        return

                    try:
                        if not inter.response.is_done():
                            await inter.response.defer(ephemeral=True)
                    except:
                        pass

                    await inter.followup.send(f"❌ Заявка {self.applicant.mention} отклонена {inter.user.mention}.", ephemeral=False)
                    await self.send_log(inter, "ОТКЛОНЕНА", 0xff0000)

                    for item in self.children:
                        item.disabled = True
                    await inter.message.edit(view=self)

                    await asyncio.sleep(5)
                    try:
                        await self.application_channel.delete(reason=f"Заявка отклонена — {inter.user}")
                    except:
                        pass

    # Остальные кнопки (на рассмотрение, обзвон) оставь как есть, только замени applicant → self.applicant

            # Отправляем заявку с кнопками
            await new_channel.send(embed=embed, view=ApplicationAdminButtons())
            await safe_respond(interaction, "✅ Заявка успешно подана! Ожидайте рассмотрения.", ephemeral=True)

        except Exception as e:
            print(f"[FormModal] Ошибка: {e}")
            await safe_respond(interaction, "❌ Произошла ошибка при подаче заявки.", ephemeral=True)



class PersonalChannelModal(Modal, title="Создать личное дело"):
    """Модалка создания личного дела — отправляет embed в личный канал пользователя (или создаёт)"""
    media_link = TextInput(
        label="Ссылка на YouTube/Imgur",
        required=True,
        placeholder="https://www.youtube.com/... или https://imgur.com/..."
    )

    async def on_submit(self, interaction: Interaction):
        try:
            guild = interaction.guild
            if not guild:
                return await safe_respond(interaction, "❌ Ошибка! Сервер не найден.", True)

            category = guild.get_channel(CATEGORY_ID)
            if not category or not isinstance(category, CategoryChannel):
                return await safe_respond(interaction, "❌ Ошибка! Категория не найдена.", True)

            # Проверка лимита каналов: пытаемся найти или создать новую категорию при необходимости
            if len(category.channels) >= 50:
                category_name_base = "Личные дела"
                new_category = None
                idx = 1
                for cat in guild.categories:
                    if cat.name.startswith(category_name_base) and len(cat.channels) < 50:
                        new_category = cat
                        break
                if not new_category:
                    while True:
                        new_name = f"{category_name_base} {idx}" if idx > 1 else category_name_base
                        try:
                            new_category = await guild.create_category(name=new_name, reason="Автосоздание категории для личных дел")
                            if category:
                                for target, perm in category.overwrites.items():
                                    await new_category.set_permissions(target, overwrite=perm)
                            break
                        except:
                            idx += 1
                category = new_category

            user_id = str(interaction.user.id)
            personal_channel = None
            if user_id in private_channels:
                ch_id = private_channels[user_id]
                personal_channel = guild.get_channel(ch_id)

            if not personal_channel:
                personal_channel = await guild.create_text_channel(
                    name=f"{interaction.user.display_name}",
                    category=category,
                    reason="Создание личного дела"
                )
                await personal_channel.set_permissions(guild.default_role, view_channel=False)
                await personal_channel.set_permissions(interaction.user, view_channel=True)
                role = guild.get_role(PRIVATE_THREAD_ROLE_ID)
                if role:
                    await personal_channel.set_permissions(role, view_channel=True)
                private_channels[user_id] = personal_channel.id
                save_private_channels()

            # Отправляем embed в личный канал
            embed = Embed(
                description=f"{interaction.user.mention}\n\n**Откат**\n ```{self.media_link.value}```",
                color=0x3A3B3C,
                timestamp=datetime.now()
            )
            embed.set_footer(text=f"Отправитель — {interaction.user.display_name}")
            await personal_channel.send(embed=embed)

            await safe_respond(interaction, f"✅ Личное дело отправлено в канал {personal_channel.mention}!", True)

        except Exception as e:
            print(f"[PersonalChannelModal] Exception: {e}")
            await safe_respond(interaction, "❌ Произошла ошибка при создании личного дела.", True)


class CreateChannelModal(Modal, title="Создать канал"):
    """Модалка создания канала — используется из Select'a"""
    def __init__(self, category: CategoryChannel):
        super().__init__(title="Создать канал")
        self.category = category
        self.channel_name = TextInput(label="Название канала", placeholder="Введите имя канала", min_length=1, max_length=50, style=TextStyle.short, required=True)
        self.add_item(self.channel_name)

    async def on_submit(self, interaction: Interaction):
        try:
            if len(self.category.channels) >= 50:
                return await safe_respond(interaction, "❌ Нельзя создать больше 50 каналов в этой категории!", True)

            name = self.channel_name.value.lower().replace(" ", "-")
            channel = await interaction.guild.create_text_channel(name=name, category=self.category, reason="Создание канала")
            await safe_respond(interaction, f"✅ Канал `{name}` создан в категории `{self.category.name}`!", True)
        except Exception as e:
            print(f"[CreateChannelModal] Exception: {e}")
            await safe_respond(interaction, "❌ Произошла ошибка при создании канала.", True)


# -------------------------
# СЕЛЕКТЫ / VIEW
# -------------------------

# 1. Сначала модалка
class VerificationRequestModal(Modal, title="Запрос на проверку"):
    reason = TextInput(
        label="Причина запроса",
        style=TextStyle.paragraph,
        placeholder="Опиши подробно, зачем тебе проверка",
        required=True,
        max_length=1000
    )

    async def on_submit(self, interaction: Interaction):
        try:
            admin_channel = interaction.guild.get_channel(VERIFICATION_ADMIN_CHANNEL_ID)
            hunter_role = interaction.guild.get_role(HUNTER_ROLE_ID)

            if not admin_channel:
                return await safe_respond(interaction, "❌ Канал админов не найден!", ephemeral=True)

            embed = discord.Embed(
                title="Новый запрос на проверку",
                description=f"**Пользователь:** {interaction.user.mention}\n**Причина:** {self.reason.value}",
                color=0x00FFFF,
                timestamp=datetime.now()
            )
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            embed.set_footer(text=f"ID: {interaction.user.id}")

            # ←←←←← ТЕГ РОЛИ НАД СООБЩЕНИЕМ С КНОПКАМИ
            await admin_channel.send(
                content=hunter_role.mention if hunter_role else "@Читхантеры",
                embed=embed,
                view=VerificationAdminButtons(interaction.user)
            )

            await safe_respond(interaction, "Запрос отправлен! Читхантеры уведомлены.", ephemeral=True)

        except Exception as e:
            print(f"[VerificationRequestModal] {e}")
            await safe_respond(interaction, "Ошибка.", ephemeral=True)

# 3. Кнопка подачи запроса
class VerificationRequestButtons(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label="Подать запрос на проверку", style=ButtonStyle.primary, emoji="🔍", custom_id="verif_req_2025")
    async def open_modal(self, interaction: Interaction, button: Button):
        await interaction.response.send_modal(VerificationRequestModal())

# -------------------------
# КНОПКИ / ВЬЮШКИ
# -------------------------
class VerificationRequestButtons(View):
    """Кнопка для подачи запроса на проверку (отправляется в verification_channel)"""
    def __init__(self):
        super().__init__(timeout=None)

    @button(label="📋 Подать запрос на проверку", style=ButtonStyle.primary, custom_id="verification_request_button_v1")
    async def verification_request_button(self, interaction: Interaction, button: Button):
        # Чтобы избежать проблем с double-response — НЕ делаем ничего перед send_modal
        await interaction.response.send_modal(VerificationRequestModal())


class PersonalChannelButtons(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label="📂 Отправить в личное дело", style=ButtonStyle.primary, custom_id="personal_channel_button_v1")
    async def personal_channel_button(self, interaction: Interaction, button: Button):
        await interaction.response.send_modal(PersonalChannelModal())


class ApplicationChannelButtons(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label="Подать заявку в семью", style=ButtonStyle.primary, emoji="📝", custom_id="apply_premium_forever")
    async def submit_app(self, interaction: Interaction, button: Button):
        await interaction.response.send_modal(FormModal())


class VerificationAdminButtons(View):
    """
    View, отправляется в канал админов вместе с embed запроса.
    Содержит две кнопки: принять / отклонить.
    """
    def __init__(self, user):
        super().__init__(timeout=None)
        self.user = user

    @button(label="✅ Принять", style=ButtonStyle.success, custom_id="accept_verification_button_v1")
    async def accept_verification_button(self, interaction: Interaction, button: Button):
        # Проверка прав
        if not interaction.user.guild_permissions.administrator and not any(role.id == ALLOWED_ROLE_ID for role in interaction.user.roles):
            return await safe_respond(interaction, "❌ У вас нет прав для принятия запросов!", True)

        try:
            notification_channel = interaction.guild.get_channel(VERIFICATION_NOTIFICATION_CHANNEL_ID)
            voice_channel = interaction.guild.get_channel(VOICE_CHANNEL_ID)

            if not notification_channel or not voice_channel:
                return await safe_respond(interaction, "❌ Ошибка! Каналы не найдены.", True)

            embed = Embed(
                title="Вызов на проверку",
                description=f" Вас вызвали для проверки.\n Пожалуйста, подключитесь к голосовому каналу:\n {voice_channel.mention}",
                color=0x3BA55D,
                timestamp=datetime.now()
            )
            embed.set_footer(text=f"Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")

            # Отправляем уведомление и отвечаем модератору
            await notification_channel.send(content=self.user.mention, embed=embed)
            await safe_respond(interaction, f"✅ Запрос {self.user.mention} принят!", True)

            # Деактивируем кнопки в сообщении, чтобы нельзя было повторно нажать
            for c in self.children:
                c.disabled = True
            try:
                await interaction.message.edit(view=self)
            except Exception:
                pass

        except Exception as e:
            print(f"[VerificationAdminButtons.accept] Exception: {e}")
            await safe_respond(interaction, "❌ Произошла ошибка при принятии запроса.", True)

    @button(label="❌ Отклонить", style=ButtonStyle.danger, custom_id="reject_verification_button_v1")
    async def reject_verification_button(self, interaction: Interaction, button: Button):
        if not interaction.user.guild_permissions.administrator and not any(role.id == ALLOWED_ROLE_ID for role in interaction.user.roles):
            return await safe_respond(interaction, "❌ У вас нет прав для отклонения запросов!", True)

        try:
            notification_channel = interaction.guild.get_channel(VERIFICATION_NOTIFICATION_CHANNEL_ID)
            if not notification_channel:
                return await safe_respond(interaction, "❌ Ошибка! Канал уведомлений не найден.", True)

            embed = Embed(
                title="Запрос на проверку отклонен",
                description=f"Запрос от {self.user.mention} был отклонен.",
                color=0xFF0000,
                timestamp=datetime.now()
            )
            embed.set_footer(text=f"Время: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")

            await notification_channel.send(embed=embed)
            await safe_respond(interaction, f"✅ Запрос {self.user.mention} отклонен!", True)

            for c in self.children:
                c.disabled = True
            try:
                await interaction.message.edit(view=self)
            except Exception:
                pass

        except Exception as e:
            print(f"[VerificationAdminButtons.reject] Exception: {e}")
            await safe_respond(interaction, "❌ Произошла ошибка при отклонении запроса.", True)

class CreateThreadModal(Modal, title="Создать ветку"):
    name = TextInput(label="Название ветки", placeholder="Капт 21.11 | Tuleshkin vs Enemy", required=True)

    async def on_submit(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)
        view = View()
        view.add_item(ThreadTargetSelect(self.name.value))
        await interaction.followup.send("В каком архиве создать ветку?", view=view, ephemeral=True)


class ThreadTargetSelect(Select):
    def __init__(self, thread_name: str):
        options = [
            SelectOption(label="Капт-архив", value=str(CAPT_ARCHIVE_ID)),
            SelectOption(label="Мкл-архив", value=str(MCL_ARCHIVE_ID)),
        ]
        super().__init__(placeholder="Выберите архив", options=options)
        self.thread_name = thread_name

    async def callback(self, interaction: Interaction):
        channel = interaction.guild.get_channel(int(self.values[0]))
        if not channel:
            return await safe_respond(interaction, "Канал не найден")
        thread = await channel.create_thread(
            name=self.thread_name[:100],
            type=discord.ChannelType.public_thread
        )
        await safe_respond(interaction, f"Ветка создана: {thread.mention}")


class TypeSelectView(View):
    def __init__(self):
        super().__init__(timeout=None)
        options = [
            SelectOption(label="КАПТ", value="capt", emoji="⚔️"),
            SelectOption(label="МКЛ", value="MCL", emoji="🔫"),
        ]
        select = Select(placeholder="Выберите тип отката", options=options)
        select.callback = self.callback
        self.add_item(select)

    async def callback(self, interaction: Interaction):
        typ = interaction.data["values"][0]
        channel_id = CAPT_ARCHIVE_ID if typ == "capt" else MCL_ARCHIVE_ID
        channel = interaction.guild.get_channel(channel_id)

        threads = list(channel.threads)
        async for thread in channel.archived_threads(limit=None):
            threads.append(thread)

        threads.sort(key=lambda t: t.created_at or datetime.min, reverse=True)

        view = ThreadSelectView(threads, typ.upper())
        await interaction.response.edit_message(content=f"Выберите ветку ({typ.upper()}):", view=view)


class ThreadSelectView(View):
    def __init__(self, threads: list[discord.Thread], type_name: str):
        super().__init__(timeout=None)
        self.type_name = type_name

        for i in range(0, len(threads), 25):
            chunk = threads[i:i+25]
            options = [SelectOption(label=t.name[:95], value=str(t.id)) for t in chunk]
            select = Select(placeholder=f"{type_name} — часть {i//25 + 1}", options=options)
            select.callback = self.select_callback
            self.add_item(select)

    async def select_callback(self, interaction: Interaction):
        thread_id = int(interaction.data["values"][0])
        thread = interaction.guild.get_channel(thread_id)
        if not thread or not isinstance(thread, discord.Thread):
            try:
                thread = await interaction.guild.fetch_channel(thread_id)
            except:
                return await safe_respond(interaction, "Ветка не найдена")
        await interaction.response.send_modal(SendRollbackToThreadModal(thread))


class SendRollbackToThreadModal(Modal, title="Отправить откат"):
    link = TextInput(label="Ссылка на YouTube / Imgur", style=TextStyle.paragraph, required=True)

    def __init__(self, thread: discord.Thread):
        super().__init__()
        self.thread = thread

    async def on_submit(self, interaction: Interaction):
        if not self.thread:
            return await safe_respond(interaction, "Ветка удалена")

        await self.thread.send(f"Откат от {interaction.user.mention}\n{self.link.value}")

        user_id = str(interaction.user.id)
        if user_id in private_channels:
            priv = interaction.guild.get_channel(private_channels[user_id])
            if priv:
                await priv.send(f"Откат → {self.thread.jump_url}\n{self.link.value}")

        await safe_respond(interaction, f"Откат отправлен в {self.thread.mention}")


class MainChannelButtons(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label="Отправить откат", style=ButtonStyle.primary, emoji="🎯", custom_id="send_rollback_final")
    async def send_rollback(self, interaction: Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("Выберите тип отката:", view=TypeSelectView(), ephemeral=True)

    @button(label="Создать ветку", style=ButtonStyle.primary, emoji="➕", custom_id="create_thread_final")
    async def create_thread(self, interaction: Interaction, button: Button):
        if not (interaction.user.guild_permissions.administrator or any(r.id == ALLOWED_ROLE_ID for r in interaction.user.roles)):
            return await safe_respond(interaction, "Нет прав", True)
        await interaction.response.send_modal(CreateThreadModal())