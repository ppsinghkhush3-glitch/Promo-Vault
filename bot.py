import telebot
import json
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import time

load_dotenv()

API_TOKEN = os.environ.get("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN, threaded=True)

OWNER_ID = "8820883004"
DEFAULT_ADMINS = [OWNER_ID, "8181451665", "8414587511", "6815389220", "7988151806"]
 
CHANNELS = [
    {"id": -1003112165120, "name": "Thirsty",      "link": "https://t.me/+F7qgYYW7xARiMzA9"},
    {"id": -1002618745933, "name": "नरक",           "link": "https://t.me/+TyB3RGxCSfU3YzA1"},
    {"id": -1003668995323, "name": "𝐋𝐄𝐆𝐄𝐍𝐃",       "link": "https://t.me/legend_vaultchat"},
    {"id": -1003847326887, "name": "सब्जी मंडी",    "link": "https://t.me/+owKZvyuQTPQwMjUx"},
    {"id": -1002741742738, "name": "𝙱 𝙳 𝙷",        "link": "https://t.me/+DrBl_OsN_F1hODAx"},
    {"id": -1003982763602, "name": "𝐀𝐧𝐧𝐞𝐁𝐞𝐥𝐥𝐚",    "link": "https://t.me/AnnebellaOfficialchat"},
]
 
MENU_ITEMS = [
    {"label": "📦 Vault",        "data": "menu_files"},
    {"label": "🔗 Links & Info", "data": "menu_links"},
    {"label": "🗺 All Menus",    "data": "menu_all"},
]
 
FILES_FILE  = "files.json"
LINKS_FILE  = "links.json"
USERS_FILE  = "users.json"
DATA_FILE   = "data.json"
ADMINS_FILE = "admins.json"
BANNED_FILE = "banned.json"
STATS_FILE  = "stats.json"
 
# ─── PERSISTENCE LAYERS ───────────────────────────────────
 
def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return default
 
def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
 
def load_admins():  return load_json(ADMINS_FILE, DEFAULT_ADMINS)
def save_admins():  save_json(ADMINS_FILE, ADMINS)
def load_banned():  return load_json(BANNED_FILE, [])
def save_banned():  save_json(BANNED_FILE, BANNED)
def load_files():   return load_json(FILES_FILE, [])
def save_files(d):  save_json(FILES_FILE, d)
def load_links():   return load_json(LINKS_FILE, [])
def save_links(d):  save_json(LINKS_FILE, d)
def load_stats():   return load_json(STATS_FILE, {"messages": 0, "files_sent": 0})
def save_stats(d):  save_json(STATS_FILE, d)
 
def load_users():
    return set(map(str, load_json(USERS_FILE, [])))
 
def save_user(user_id):
    users = load_users()
    users.add(str(user_id))
    save_json(USERS_FILE, list(users))
 
def get_all_users():
    return load_users()
 
def load_data():
    return load_json(DATA_FILE, {"user_channels": {}})
 
def save_data(data):
    save_json(DATA_FILE, data)
 
ADMINS = [str(a) for a in load_admins()]
BANNED = [str(b) for b in load_banned()]
 
# ─── AUTHORIZATION UTILS ──────────────────────────────────
 
def is_owner(uid): return str(uid) == str(OWNER_ID)
def is_admin(uid): return str(uid) in ADMINS or is_owner(uid)
def is_banned(uid): return str(uid) in BANNED
 
def increment_stat(key):
    stats = load_stats()
    stats[key] = stats.get(key, 0) + 1
    save_stats(stats)
 
def ban_gate(msg_or_call):
    if hasattr(msg_or_call, "from_user"):
        uid = msg_or_call.from_user.id
        cid = msg_or_call.chat.id if hasattr(msg_or_call, "chat") else msg_or_call.message.chat.id
    else:
        return False
    if is_banned(uid) and not is_owner(uid):
        bot.send_message(cid, "🚫 You are banned from using this bot.")
        return True
    return False
 
# ─── KEYBOARDS ────────────────────────────────────────────
 
def channels_keyboard():
    """Shows all channels as join buttons + I've Joined button at bottom."""
    markup = InlineKeyboardMarkup()
    for ch in CHANNELS:
        markup.add(InlineKeyboardButton(f"🔗 {ch['name']}", url=ch['link']))
    markup.add(InlineKeyboardButton("✅ I've Joined All — Open Menu", callback_data="open_main_menu"))
    return markup
 
def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = [InlineKeyboardButton(i["label"], callback_data=i["data"]) for i in MENU_ITEMS]
    markup.add(*buttons)
    return markup
 
def all_menus_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("📦 Vault",        callback_data="menu_files"),
        InlineKeyboardButton("🔗 Links & Info", callback_data="menu_links"),
        InlineKeyboardButton("📜 Rules",        callback_data="menu_rules"),
        InlineKeyboardButton("👤 Contact",      callback_data="menu_contact"),
        InlineKeyboardButton("🔙 Back",         callback_data="menu_back"),
    )
    return markup
 
def owner_panel_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("👥 Admins",       callback_data="op_admins"),
        InlineKeyboardButton("🚫 Banned",       callback_data="op_banned"),
        InlineKeyboardButton("📊 Stats",        callback_data="op_stats"),
        InlineKeyboardButton("👤 User Info",    callback_data="op_userinfo"),
        InlineKeyboardButton("📢 Broadcast",    callback_data="op_broadcast"),
        InlineKeyboardButton("🗑 Clear Vault",  callback_data="op_clearvault"),
        InlineKeyboardButton("🔗 Clear Links",  callback_data="op_clearlinks"),
        InlineKeyboardButton("📋 Commands",     callback_data="op_commands"),
    )
    return markup
 
def admin_panel_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📦 List Files",  callback_data="ap_listfiles"),
        InlineKeyboardButton("🔗 List Links",  callback_data="ap_listlinks"),
        InlineKeyboardButton("📊 Stats",       callback_data="ap_stats"),
        InlineKeyboardButton("📢 Broadcast",   callback_data="ap_broadcast"),
        InlineKeyboardButton("📋 Commands",    callback_data="ap_commands"),
    )
    return markup
 
# ─── MENU RENDERERS ───────────────────────────────────────
 
def send_main_menu(chat_id, name):
    """Send clean main menu — shown after user taps I've Joined."""
    bot.send_message(
        chat_id,
        f"👋 *Welcome, {name}!* Access Granted.\n\n"
        "━━━━━━━━━━━━━━━\n"
        "📦 Vault — all files\n"
        "🔗 Links — sources & info\n"
        "🗺 All Menus — full navigation\n"
        "━━━━━━━━━━━━━━━\n\n"
        "Choose an option below 👇",
        parse_mode="Markdown",
        reply_markup=main_menu(),
        disable_web_page_preview=True
    )
 
def show_main_menu_edit(call):
    name = call.from_user.first_name or "User"
    text = (
        f"👋 *Welcome, {name}!*\n\n"
        "🔓 *Access Granted*\n"
        "━━━━━━━━━━━━━━━\n"
        "📦 *Vault* — all files\n"
        "🔗 *Links* — sources & info\n"
        "🗺 *Menus* — full navigation\n"
        "━━━━━━━━━━━━━━━\n\n"
        "Choose an option below 👇"
    )
    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=main_menu()
        )
    except Exception:
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=main_menu())
 
# ─── CORE COMMAND HANDLERS ────────────────────────────────
 
@bot.message_handler(commands=["start"])
def start(msg):
    # 1. Ban check
    if ban_gate(msg):
        return
 
    # 2. Redirect groups to PM
    if msg.chat.type in ["group", "supergroup"]:
        bot_username = bot.get_me().username
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🚀 Open in PM", url=f"https://t.me/{bot_username}?start=true"))
        bot.send_message(msg.chat.id,
                         f"👋 Hi {msg.from_user.first_name}! Please start me in private to access the vault.",
                         reply_markup=markup)
        return
 
    user_id = msg.from_user.id
    name = msg.from_user.first_name or "User"
 
    # 3. Logging
    save_user(user_id)
    increment_stat("messages")
 
    # 4. Deep-link handling (e.g. t.me/bot?start=join_123)
    args = msg.text.split()
    if len(args) > 1 and args[1].startswith("join_"):
        try:
            target_id_str = args[1].replace("join_", "")
            target_ch = next((ch for ch in CHANNELS if str(abs(ch["id"])) == target_id_str), None)
            if target_ch:
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("🚀 Open Channel", url=target_ch["link"]))
                bot.send_message(msg.chat.id, f"✨ Opening *{target_ch['name']}*...",
                                 parse_mode="Markdown", reply_markup=markup)
                return
        except Exception:
            pass
 
    # 5. Owner
    if is_owner(user_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("⚙️ Owner Panel", callback_data="owner_panel"))
        bot.send_message(msg.chat.id,
                         f"👑 *Welcome, Owner {name}!*\n\n"
                         "━━━━━━━━━━━━━━━\n"
                         "Use `/ownercmd` to check full administration commands.",
                         parse_mode="Markdown", reply_markup=markup)
        return
 
    # 6. Admin
    if is_admin(user_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🛠 Admin Panel", callback_data="admin_panel"))
        bot.send_message(msg.chat.id,
                         f"🛠 *Welcome, Admin {name}!*\n\n"
                         "━━━━━━━━━━━━━━━\n"
                         "Use `/admincmd` to view authorization guidelines.",
                         parse_mode="Markdown", reply_markup=markup)
        return
 
    # 7. Regular user — show channels with "I've Joined" button
    channels_text = "\n".join([f"• [{ch['name']}]({ch['link']})" for ch in CHANNELS])
    bot.send_message(
        msg.chat.id,
        f"👋 *Welcome, {name}!*\n\n"
        "📢 *Join Our Channels:*\n"
        "━━━━━━━━━━━━━━━\n"
        f"{channels_text}\n"
        "━━━━━━━━━━━━━━━\n\n"
        "After joining, tap the button below to open the menu 👇",
        parse_mode="Markdown",
        reply_markup=channels_keyboard(),
        disable_web_page_preview=True
    )
 
 
@bot.message_handler(commands=["ownercmd"])
def owner_commands_msg(msg):
    if not is_owner(msg.from_user.id):
        bot.send_message(msg.chat.id, "❌ Owner authorization required.")
        return
    text = (
        "👑 *Owner Complete Commands Matrix*\n"
        "━━━━━━━━━━━━━━━\n"
        "👥 *Access Controls:*\n"
        "• `/addadmin <id>` — Authorize target profile\n"
        "• `/removeadmin <id>` — Strip admin authorization\n"
        "• `/admins` — Display admin listing\n\n"
        "🚫 *Banhammer:*\n"
        "• `/ban <id>` — Ban user\n"
        "• `/unban <id>` — Unban user\n"
        "• `/banned` — List banned users\n\n"
        "📊 *System Metrics:*\n"
        "• `/broadcast` — Broadcast (reply to a message)\n"
        "• `/stats` — View stats\n"
        "• `/usercount` — Total users\n\n"
        "📁 *Channel Management:*\n"
        "• `/addchannel id | name | link` — Add channel\n"
        "• `/removechannel <id>` — Remove channel\n"
        "• `/listchannels` — List channels\n\n"
        "🗑️ *Database:*\n"
        "• `/clearvault` — Wipe vault\n"
        "• `/clearlinks` — Clear links\n"
        "• `/ping` — Check bot latency"
    )
    try:
        bot.send_message(msg.chat.id, text, parse_mode="Markdown")
    except Exception as e:
        print(f"Markdown Error: {e}")
        bot.send_message(msg.chat.id, text.replace("*", "").replace("`", ""))
 
 
@bot.message_handler(commands=["admincmd"])
def admin_commands_msg(msg):
    if not is_admin(msg.from_user.id):
        bot.send_message(msg.chat.id, "❌ Access denied.")
        return
    text = (
        "🛠️ *Admin Commands*\n"
        "━━━━━━━━━━━━━━━\n"
        "📢 `/broadcast` — Broadcast (reply to message)\n"
        "📊 `/stats` — View stats\n"
        "📁 `/addfile file_id | Name` — Add file to vault\n"
        "🗑️ `/removefile <file_id>` — Remove file\n"
        "📋 `/listfiles` — List vault files\n"
        "🔗 `/addlink Label | URL` — Add link\n"
        "➖ `/removelink <url>` — Remove link\n"
        "📋 `/listlinks` — List links"
    )
    bot.send_message(msg.chat.id, text, parse_mode="Markdown")
 
# ─── CHANNEL JOIN BUTTON CALLBACK ────────────────────────
 
@bot.callback_query_handler(func=lambda c: c.data == "open_main_menu")
def open_main_menu(call):
    if ban_gate(call): return
    bot.answer_callback_query(call.id, "✅ Welcome!", show_alert=False)
    name = call.from_user.first_name or "User"
    text = (
        f"👋 *Welcome, {name}!* Access Granted.\n\n"
        "━━━━━━━━━━━━━━━\n"
        "📦 Vault — all files\n"
        "🔗 Links — sources & info\n"
        "🗺 All Menus — full navigation\n"
        "━━━━━━━━━━━━━━━\n\n"
        "Choose an option below 👇"
    )
    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=main_menu()
        )
    except Exception:
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=main_menu())
 
# ─── PANEL CALLBACKS ──────────────────────────────────────
 
@bot.callback_query_handler(func=lambda c: c.data == "owner_panel")
def cb_owner_panel(call):
    bot.answer_callback_query(call.id)
    if not is_owner(call.from_user.id): return
    bot.send_message(call.message.chat.id, "👑 *Owner Dashboard*\nSelect an option:",
                     parse_mode="Markdown", reply_markup=owner_panel_keyboard())
 
@bot.callback_query_handler(func=lambda c: c.data == "admin_panel")
def cb_admin_panel(call):
    bot.answer_callback_query(call.id)
    if not is_admin(call.from_user.id): return
    bot.send_message(call.message.chat.id, "🛠 *Admin Dashboard*\nSelect an option:",
                     parse_mode="Markdown", reply_markup=admin_panel_keyboard())
 
@bot.callback_query_handler(func=lambda c: c.data == "op_admins")
def op_admins(call):
    bot.answer_callback_query(call.id)
    if not is_owner(call.from_user.id): return
    text = "👥 *Admin List:*\n" + ("\n".join(f"• `{a}`" for a in ADMINS) if ADMINS else "No admins set.")
    bot.send_message(call.message.chat.id, text, parse_mode="Markdown")
 
@bot.callback_query_handler(func=lambda c: c.data == "op_banned")
def op_banned(call):
    bot.answer_callback_query(call.id)
    if not is_owner(call.from_user.id): return
    text = "🚫 *Banned Users:*\n" + ("\n".join(f"• `{b}`" for b in BANNED) if BANNED else "No banned users.")
    bot.send_message(call.message.chat.id, text, parse_mode="Markdown")
 
@bot.callback_query_handler(func=lambda c: c.data in ("op_stats", "ap_stats"))
def op_stats(call):
    bot.answer_callback_query(call.id)
    if not is_admin(call.from_user.id): return
    stats = load_stats()
    bot.send_message(call.message.chat.id,
        f"📊 *Stats*\n\n"
        f"👤 Users: `{len(get_all_users())}`\n"
        f"💬 Messages: `{stats.get('messages', 0)}`\n"
        f"📁 Files Sent: `{stats.get('files_sent', 0)}`\n"
        f"📦 Vault Items: `{len(load_files())}`\n"
        f"🔗 Links: `{len(load_links())}`", parse_mode="Markdown")
 
@bot.callback_query_handler(func=lambda c: c.data == "op_userinfo")
def op_userinfo(call):
    bot.answer_callback_query(call.id)
    if not is_owner(call.from_user.id): return
    bot.send_message(call.message.chat.id, "📥 Send the user ID to look up:")
    bot.register_next_step_handler_by_chat_id(call.message.chat.id, fetch_user_info)
 
def fetch_user_info(msg):
    if not is_owner(msg.from_user.id): return
    try:
        target = msg.text.strip()
        users  = get_all_users()
        in_db  = target in users
        banned = target in BANNED
        admin  = target in ADMINS
        owner  = target == OWNER_ID
        bot.send_message(msg.chat.id,
            f"👤 *User: `{target}`*\n\n"
            f"In Database: {'✅ Yes' if in_db else '❌ No'}\n"
            f"Role: {'👑 Owner' if owner else '🛠 Admin' if admin else '👤 User'}\n"
            f"Banned: {'🚫 Yes' if banned else '🟢 No'}", parse_mode="Markdown")
    except Exception:
        bot.send_message(msg.chat.id, "❌ Failed to fetch user info.")
 
@bot.callback_query_handler(func=lambda c: c.data in ("op_broadcast", "ap_broadcast"))
def op_broadcast_cb(call):
    bot.answer_callback_query(call.id)
    if not is_admin(call.from_user.id): return
    bot.send_message(call.message.chat.id, "✍️ Send the broadcast message now:")
    bot.register_next_step_handler_by_chat_id(call.message.chat.id, do_broadcast_text)
 
def do_broadcast_text(msg):
    if not is_admin(msg.from_user.id): return
    if msg.text and (msg.text.startswith("/") or msg.text.startswith("!")):
        bot.send_message(msg.chat.id, "❌ Aborted. Commands cannot be broadcast.")
        return
    users = get_all_users()
    success, failed = 0, 0
    for uid in users:
        try:
            bot.copy_message(uid, msg.chat.id, msg.message_id)
            success += 1
        except Exception:
            failed += 1
    bot.send_message(msg.chat.id, f"📢 Broadcast done.\n✅ Sent: {success} | ❌ Failed: {failed}")
 
@bot.callback_query_handler(func=lambda c: c.data == "op_clearvault")
def op_clearvault(call):
    bot.answer_callback_query(call.id)
    if not is_owner(call.from_user.id): return
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("🗑 Confirm Wipe", callback_data="confirm_clearvault"),
        InlineKeyboardButton("❌ Cancel",       callback_data="cancel_action")
    )
    bot.send_message(call.message.chat.id,
                     "⚠️ This will permanently delete all vault files. Continue?", reply_markup=markup)
 
@bot.callback_query_handler(func=lambda c: c.data == "confirm_clearvault")
def confirm_clearvault(call):
    bot.answer_callback_query(call.id)
    if not is_owner(call.from_user.id): return
    save_files([])
    bot.edit_message_text("✅ Vault wiped successfully.", call.message.chat.id, call.message.message_id)
 
@bot.callback_query_handler(func=lambda c: c.data == "op_clearlinks")
def op_clearlinks(call):
    bot.answer_callback_query(call.id)
    if not is_owner(call.from_user.id): return
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("🗑 Confirm Clear", callback_data="confirm_clearlinks"),
        InlineKeyboardButton("❌ Cancel",        callback_data="cancel_action")
    )
    bot.send_message(call.message.chat.id,
                     "⚠️ This will permanently delete all saved links. Continue?", reply_markup=markup)
 
@bot.callback_query_handler(func=lambda c: c.data == "confirm_clearlinks")
def confirm_clearlinks(call):
    bot.answer_callback_query(call.id)
    if not is_owner(call.from_user.id): return
    save_links([])
    bot.edit_message_text("✅ All links cleared.", call.message.chat.id, call.message.message_id)
 
@bot.callback_query_handler(func=lambda c: c.data == "cancel_action")
def cancel_action(call):
    bot.answer_callback_query(call.id, "Cancelled.")
    bot.edit_message_text("❌ Action cancelled.", call.message.chat.id, call.message.message_id)
 
@bot.callback_query_handler(func=lambda c: c.data == "op_commands")
def op_commands_panel_callback(call):
    bot.answer_callback_query(call.id)
    if not is_owner(call.from_user.id): return
    class W:
        def __init__(self, c):
            self.from_user = c.from_user
            self.chat = c.message.chat
    owner_commands_msg(W(call))
 
@bot.callback_query_handler(func=lambda c: c.data == "ap_commands")
def ap_commands_panel_callback(call):
    bot.answer_callback_query(call.id)
    if not is_admin(call.from_user.id): return
    class W:
        def __init__(self, c):
            self.from_user = c.from_user
            self.chat = c.message.chat
    admin_commands_msg(W(call))
 
@bot.callback_query_handler(func=lambda c: c.data == "ap_listfiles")
def ap_listfiles(call):
    bot.answer_callback_query(call.id)
    if not is_admin(call.from_user.id): return
    files = load_files()
    if not files:
        bot.send_message(call.message.chat.id, "📦 Vault is empty.")
        return
    text = "📋 *Vault Files:*\n\n" + "\n".join(
        f"{i+1}. `{f['name']}`\n↳ `{f['file_id']}`" for i, f in enumerate(files))
    bot.send_message(call.message.chat.id, text, parse_mode="Markdown")
 
@bot.callback_query_handler(func=lambda c: c.data == "ap_listlinks")
def ap_listlinks(call):
    bot.answer_callback_query(call.id)
    if not is_admin(call.from_user.id): return
    links = load_links()
    if not links:
        bot.send_message(call.message.chat.id, "🔗 No links saved.")
        return
    text = "📋 *Saved Links:*\n\n" + "\n".join(
        f"{i+1}. *{l['label']}* — [Open]({l['url']})" for i, l in enumerate(links))
    bot.send_message(call.message.chat.id, text, parse_mode="Markdown", disable_web_page_preview=True)
 
# ─── USER MENU CALLBACKS ──────────────────────────────────
 
@bot.callback_query_handler(func=lambda c: c.data == "menu_files")
def menu_files(call):
    if ban_gate(call): return
    bot.answer_callback_query(call.id)
    files = load_files()
    if not files:
        bot.send_message(call.message.chat.id, "📦 Vault is currently empty.")
        return
    bot.send_message(call.message.chat.id, "📦 *Vault — Sending files...* 👇", parse_mode="Markdown")
    for f in files:
        try:
            bot.send_document(call.message.chat.id, f["file_id"], caption=f"📁 {f['name']}")
            increment_stat("files_sent")
        except Exception:
            pass
 
@bot.callback_query_handler(func=lambda c: c.data == "menu_links")
def menu_links(call):
    if ban_gate(call): return
    bot.answer_callback_query(call.id)
    links  = load_links()
    markup = InlineKeyboardMarkup()
    for l in links:
        markup.add(InlineKeyboardButton(l["label"], url=l["url"]))
    markup.add(InlineKeyboardButton("👤 Contact Admin", url="https://t.me/kaalnova"))
    markup.add(InlineKeyboardButton("🔙 Back", callback_data="menu_back"))
    bot.send_message(call.message.chat.id, "🔗 *Links & Info* 👇",
                     parse_mode="Markdown", reply_markup=markup)
 
@bot.callback_query_handler(func=lambda c: c.data == "menu_all")
def menu_all(call):
    if ban_gate(call): return
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "🗺 *All Menus* — Select a section:",
                     parse_mode="Markdown", reply_markup=all_menus_keyboard())
 
@bot.callback_query_handler(func=lambda c: c.data == "menu_rules")
def menu_rules(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id,
                     "📜 *Rules*\n\n"
                     "1. Respect all members.\n"
                     "2. No spam or flooding.\n"
                     "3. Follow admin directives.", parse_mode="Markdown")
 
@bot.callback_query_handler(func=lambda c: c.data == "menu_contact")
def menu_contact(call):
    bot.answer_callback_query(call.id)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("👤 Message Admin", url="https://t.me/kaalnova"))
    bot.send_message(call.message.chat.id, "👤 *Contact Support*",
                     parse_mode="Markdown", reply_markup=markup)
 
@bot.callback_query_handler(func=lambda c: c.data == "menu_back")
def menu_back(call):
    bot.answer_callback_query(call.id)
    show_main_menu_edit(call)
 
# ─── OWNER/ADMIN COMMAND HANDLERS ─────────────────────────
 
@bot.message_handler(commands=["addadmin"])
def add_admin(msg):
    if not is_owner(msg.from_user.id):
        bot.send_message(msg.chat.id, "❌ Owner only."); return
    parts = msg.text.split()
    if len(parts) < 2:
        bot.send_message(msg.chat.id, "Usage: `/addadmin <user_id>`", parse_mode="Markdown"); return
    new_admin = parts[1].strip()
    if new_admin not in ADMINS:
        ADMINS.append(new_admin)
        save_admins()
        bot.send_message(msg.chat.id, f"✅ Added admin: `{new_admin}`", parse_mode="Markdown")
    else:
        bot.send_message(msg.chat.id, "ℹ️ Already an admin.")
 
@bot.message_handler(commands=["removeadmin"])
def remove_admin(msg):
    if not is_owner(msg.from_user.id):
        bot.send_message(msg.chat.id, "❌ Owner only."); return
    parts = msg.text.split()
    if len(parts) < 2:
        bot.send_message(msg.chat.id, "Usage: `/removeadmin <user_id>`", parse_mode="Markdown"); return
    rem = parts[1].strip()
    if str(rem) == str(OWNER_ID):
        bot.send_message(msg.chat.id, "🚫 Cannot remove the owner."); return
    if rem in ADMINS:
        ADMINS.remove(rem)
        save_admins()
        bot.send_message(msg.chat.id, f"✅ Removed admin: `{rem}`", parse_mode="Markdown")
    else:
        bot.send_message(msg.chat.id, "❌ Not found in admin list.")
 
@bot.message_handler(commands=["admins"])
def list_admins(msg):
    if not is_owner(msg.from_user.id):
        bot.send_message(msg.chat.id, "❌ Owner only."); return
    text = "👥 *Admins:*\n" + ("\n".join(f"• `{a}`" for a in ADMINS) if ADMINS else "None.")
    bot.send_message(msg.chat.id, text, parse_mode="Markdown")
 
@bot.message_handler(commands=["ban"])
def ban_user(msg):
    if not is_owner(msg.from_user.id):
        bot.send_message(msg.chat.id, "❌ Owner only."); return
    parts = msg.text.split()
    if len(parts) < 2:
        bot.send_message(msg.chat.id, "Usage: `/ban <user_id>`", parse_mode="Markdown"); return
    target = parts[1].strip()
    if str(target) == str(OWNER_ID):
        bot.send_message(msg.chat.id, "❌ Cannot ban yourself."); return
    if target not in BANNED:
        BANNED.append(target)
        save_banned()
        bot.send_message(msg.chat.id, f"🚫 Banned: `{target}`", parse_mode="Markdown")
    else:
        bot.send_message(msg.chat.id, "ℹ️ Already banned.")
 
@bot.message_handler(commands=["unban"])
def unban_user(msg):
    if not is_owner(msg.from_user.id):
        bot.send_message(msg.chat.id, "❌ Owner only."); return
    parts = msg.text.split()
    if len(parts) < 2:
        bot.send_message(msg.chat.id, "Usage: `/unban <user_id>`", parse_mode="Markdown"); return
    target = parts[1].strip()
    if target in BANNED:
        BANNED.remove(target)
        save_banned()
        bot.send_message(msg.chat.id, f"✅ Unbanned: `{target}`", parse_mode="Markdown")
    else:
        bot.send_message(msg.chat.id, "❌ Not in ban list.")
 
@bot.message_handler(commands=["banned"])
def list_banned_users_msg(msg):
    if not is_owner(msg.from_user.id):
        bot.send_message(msg.chat.id, "❌ Owner only."); return
    text = "🚫 *Banned Users:*\n" + ("\n".join(f"• `{b}`" for b in BANNED) if BANNED else "None.")
    bot.send_message(msg.chat.id, text, parse_mode="Markdown")
 
@bot.message_handler(commands=["stats"])
def show_stats_msg(msg):
    if not is_admin(msg.from_user.id):
        bot.send_message(msg.chat.id, "❌ Admin only."); return
    stats = load_stats()
    bot.send_message(msg.chat.id,
        f"📊 *Stats*\n\n"
        f"👤 Users: `{len(get_all_users())}`\n"
        f"💬 Messages: `{stats.get('messages', 0)}`\n"
        f"📁 Files Sent: `{stats.get('files_sent', 0)}`\n"
        f"📦 Vault Items: `{len(load_files())}`\n"
        f"🔗 Links: `{len(load_links())}`", parse_mode="Markdown")
 
@bot.message_handler(commands=["usercount"])
def structural_usercount_msg(msg):
    if not is_owner(msg.from_user.id):
        bot.send_message(msg.chat.id, "❌ Owner only."); return
    bot.send_message(msg.chat.id, f"📊 *Total Users:* `{len(get_all_users())}`", parse_mode="Markdown")
 
@bot.message_handler(commands=["addfile"])
def add_file_via_command(msg):
    if not is_admin(msg.from_user.id):
        bot.send_message(msg.chat.id, "❌ Admin only."); return
    parts = msg.text.split(maxsplit=2)
    if len(parts) < 3:
        bot.send_message(msg.chat.id, "Usage: `/addfile <file_id> | <name>`", parse_mode="Markdown"); return
    fid   = parts[1].strip()
    fname = parts[2].replace("|", "").strip()
    files = load_files()
    files.append({"file_id": fid, "name": fname})
    save_files(files)
    bot.send_message(msg.chat.id, f"✅ File added: `{fname}`", parse_mode="Markdown")
 
@bot.message_handler(commands=["removefile"])
def remove_file_via_command(msg):
    if not is_admin(msg.from_user.id):
        bot.send_message(msg.chat.id, "❌ Admin only."); return
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(msg.chat.id, "Usage: `/removefile <file_id>`", parse_mode="Markdown"); return
    fid      = parts[1].strip()
    files    = load_files()
    filtered = [f for f in files if f["file_id"] != fid]
    if len(files) == len(filtered):
        bot.send_message(msg.chat.id, "❌ File not found."); return
    save_files(filtered)
    bot.send_message(msg.chat.id, "✅ File removed.")
 
@bot.message_handler(commands=["listfiles"])
def list_files_cmd_wrapper(msg):
    if not is_admin(msg.from_user.id): return
    files = load_files()
    if not files:
        bot.send_message(msg.chat.id, "📦 Vault is empty."); return
    text = "📋 *Vault Files:*\n\n" + "\n".join(
        f"{i+1}. *{f['name']}*\n↳ `{f['file_id']}`" for i, f in enumerate(files))
    bot.send_message(msg.chat.id, text, parse_mode="Markdown")
 
@bot.message_handler(commands=["addlink"])
def add_link_via_command(msg):
    if not is_admin(msg.from_user.id):
        bot.send_message(msg.chat.id, "❌ Admin only."); return
    raw_args = msg.text.replace("/addlink", "").strip()
    if "|" not in raw_args:
        bot.send_message(msg.chat.id, "Usage: `/addlink Label | https://url`", parse_mode="Markdown"); return
    parts = raw_args.split("|", 1)
    label = parts[0].strip()
    url   = parts[1].strip()
    links = load_links()
    links.append({"label": label, "url": url})
    save_links(links)
    bot.send_message(msg.chat.id, f"✅ Link added: *{label}*", parse_mode="Markdown")
 
@bot.message_handler(commands=["removelink"])
def remove_link_via_command(msg):
    if not is_admin(msg.from_user.id): return
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(msg.chat.id, "Usage: `/removelink <url>`", parse_mode="Markdown"); return
    target_url = parts[1].strip()
    links      = load_links()
    filtered   = [l for l in links if l["url"] != target_url]
    if len(links) == len(filtered):
        bot.send_message(msg.chat.id, "❌ URL not found."); return
    save_links(filtered)
    bot.send_message(msg.chat.id, "✅ Link removed.")
 
@bot.message_handler(commands=["listlinks"])
def list_links_cmd_wrapper(msg):
    if not is_admin(msg.from_user.id): return
    links = load_links()
    if not links:
        bot.send_message(msg.chat.id, "🔗 No links saved."); return
    text = "📋 *Saved Links:*\n\n" + "\n".join(
        f"{i+1}. *{l['label']}* — [Open]({l['url']})" for i, l in enumerate(links))
    bot.send_message(msg.chat.id, text, parse_mode="Markdown", disable_web_page_preview=True)
 
@bot.message_handler(commands=["addchannel"])
def add_channel_via_command(msg):
    if not is_owner(msg.from_user.id):
        bot.send_message(msg.chat.id, "❌ Owner only."); return
    raw_args = msg.text.replace("/addchannel", "").strip()
    if "|" not in raw_args or len(raw_args.split("|")) < 3:
        bot.send_message(msg.chat.id,
            "Usage: `/addchannel -100XXXXXX | Name | https://t.me/link`", parse_mode="Markdown"); return
    parts = raw_args.split("|")
    try:
        cid   = int(parts[0].strip())
        cname = parts[1].strip()
        clink = parts[2].strip()
        global CHANNELS
        CHANNELS.append({"id": cid, "name": cname, "link": clink})
        bot.send_message(msg.chat.id, f"✅ Channel added: *{cname}* (`{cid}`)", parse_mode="Markdown")
    except Exception:
        bot.send_message(msg.chat.id, "❌ Invalid format. Channel ID must be a negative integer.")
 
@bot.message_handler(commands=["removechannel"])
def remove_channel_via_command(msg):
    if not is_owner(msg.from_user.id): return
    parts = msg.text.split()
    if len(parts) < 2:
        bot.send_message(msg.chat.id, "Usage: `/removechannel <channel_id>`", parse_mode="Markdown"); return
    try:
        target_id = int(parts[1].strip())
        global CHANNELS
        initial_len = len(CHANNELS)
        CHANNELS = [ch for ch in CHANNELS if ch["id"] != target_id]
        if len(CHANNELS) == initial_len:
            bot.send_message(msg.chat.id, "❌ Channel not found."); return
        bot.send_message(msg.chat.id, f"✅ Channel removed: `{target_id}`", parse_mode="Markdown")
    except Exception:
        bot.send_message(msg.chat.id, "❌ Invalid channel ID.")
 
@bot.message_handler(commands=["listchannels"])
def list_channels_cmd_wrapper(msg):
    if not is_owner(msg.from_user.id): return
    if not CHANNELS:
        bot.send_message(msg.chat.id, "📋 No channels configured."); return
    text = "📋 *Channels:*\n\n" + "\n".join(
        f"{i+1}. *{ch['name']}* (`{ch['id']}`)\n↳ [Link]({ch['link']})" for i, ch in enumerate(CHANNELS))
    bot.send_message(msg.chat.id, text, parse_mode="Markdown", disable_web_page_preview=True)
 
@bot.message_handler(commands=["clearvault"])
def clear_vault_command_wrapper(msg):
    if not is_owner(msg.from_user.id): return
    class DummyCall:
        def __init__(self, m):
            self.message = m; self.from_user = m.from_user; self.id = "0"
    op_clearvault(DummyCall(msg))
 
@bot.message_handler(commands=["clearlinks"])
def clear_links_command_wrapper(msg):
    if not is_owner(msg.from_user.id): return
    class DummyCall:
        def __init__(self, m):
            self.message = m; self.from_user = m.from_user; self.id = "0"
    op_clearlinks(DummyCall(msg))
 
@bot.message_handler(commands=["broadcast"])
def broadcast_command_wrapper(msg):
    if not is_admin(msg.from_user.id):
        bot.send_message(msg.chat.id, "❌ Admin only."); return
    if not msg.reply_to_message:
        bot.send_message(msg.chat.id, "⚠️ Reply to a message to broadcast it."); return
    users = get_all_users()
    bot.send_message(msg.chat.id, f"🚀 Broadcasting to `{len(users)}` users...")
    success, failed = 0, 0
    for uid in users:
        try:
            bot.copy_message(uid, msg.chat.id, msg.reply_to_message.message_id)
            success += 1
        except Exception:
            failed += 1
    bot.send_message(msg.chat.id,
        f"📢 *Broadcast Complete*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"✅ Sent: `{success}`\n"
        f"❌ Failed: `{failed}`", parse_mode="Markdown")
 
@bot.message_handler(commands=["ping"])
def ping_bot(msg):
    if not is_owner(msg.from_user.id): return
    bot.reply_to(msg, "🚀 *PONG!* Bot is online.", parse_mode="Markdown")
 
# ─── MEDIA HANDLER (file_id extraction for admins) ────────
 
@bot.message_handler(content_types=["document", "photo", "video", "audio", "voice"])
def get_file_id(msg):
    if ban_gate(msg): return
    if not is_admin(msg.from_user.id):
        return  # Regular users sending media — ignore silently
    if   msg.document: fid = msg.document.file_id
    elif msg.photo:    fid = msg.photo[-1].file_id
    elif msg.video:    fid = msg.video.file_id
    elif msg.audio:    fid = msg.audio.file_id
    elif msg.voice:    fid = msg.voice.file_id
    else: return
    bot.reply_to(msg, f"✅ `file_id`:\n`{fid}`", parse_mode="Markdown")
 
# ─── FALLBACK HANDLER ─────────────────────────────────────
 
@bot.message_handler(func=lambda msg: True)
def gate(msg):
    if ban_gate(msg): return
    if is_admin(msg.from_user.id): return
    increment_stat("messages")
    bot.send_message(msg.chat.id, "Use /start to open the menu.")
 
# ─── RUNTIME ──────────────────────────────────────────────
if __name__ == "__main__":
    print("Bot started. Polling...")
    while True:
        try:
            bot.infinity_polling(
                timeout=60,
                long_polling_timeout=30
            )
        except Exception as e:
            print(f"Polling crashed: {e}")
            print("Restarting in 5 seconds...")
            time.sleep(5)
