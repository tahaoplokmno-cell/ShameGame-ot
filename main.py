
import os
# تثبيت المكتبات اللازمة تلقائياً عند تشغيل السيرفر
os.system("pip install pyTelegramBotAPI")

import telebot
from telebot import types

TOKEN = "8946618106:AAH5J1vADNZ-YDGGv0CXfzSTjQuFa0Cgnjs"
ADMIN_ID = 8243108672  

bot = telebot.TeleBot(TOKEN)

# إعدادات المتجر الأساسية التي أرسلتها
EXCHANGE_RATE = 14750  # 💰 سعر الصرف (1$ = 14,750 ل.س)
SHAM_CASH_WALLET = "8bf19e519ba13641f2a8ae981b8f3081" # 💳 رقم محفظة شام كاش
SUPPORT_NUMBER = "939965929" # 📞 رقم الدعم الفني

# الذاكرة الرقمية لحسابات المتجر والطلبات
users_db = {} 
pending_orders = {} 
orders_count = 8500  

# 📋 الأقسام وقائمة الأسعار الحقيقية لمتجرك محسوبة بالدولار ومحولة تلقائياً بالليرة
CATEGORIES = {
    "pubg": "🎮 شدات ببجي موبايل",
    "ff": "🔥 فري فاير (شرق أوسط Garena)",
    "cod": "🔫 كول اوف ديوتي",
    "ml": "⚔️ موبايل ليجندز (Global)",
    "coc": "🏰 كلاش اوف كلانس",
    "roblox": "🧱 روبلوكس (أكواد أمريكية)"
}

PRODUCTS = {
    # ببجي
    "pubg_1": {"category": "pubg", "name": "60 شدة UC", "price_usd": 1.0},
    "pubg_2": {"category": "pubg", "name": "325 شدة UC", "price_usd": 5.0},
    "pubg_3": {"category": "pubg", "name": "660 شدة UC", "price_usd": 9.80},
    # فري فاير
    "ff_1": {"category": "ff", "name": "100 + 10 مجوهرات", "price_usd": 1.0},
    "ff_2": {"category": "ff", "name": "210 + 21 مجوهرات", "price_usd": 2.0},
    "ff_3": {"category": "ff", "name": "530 + 53 مجوهرات", "price_usd": 5.0},
    # كول اوف ديوتي
    "cod_1": {"category": "cod", "name": "320 CP", "price_usd": 5.0},
    "cod_2": {"category": "cod", "name": "480 CP", "price_usd": 7.30},
    # موبايل ليجندز
    "ml_1": {"category": "ml", "name": "172 Diamond", "price_usd": 2.90},
    "ml_2": {"category": "ml", "name": "257 Diamond", "price_usd": 4.0},
    # كلاش اوف كلانس
    "coc_1": {"category": "coc", "name": "88 جواهر", "price_usd": 1.30},
    "coc_2": {"category": "coc", "name": "500 جواهر", "price_usd": 6.60},
    # روبلوكس
    "roblox_1": {"category": "roblox", "name": "بطاقة كود 10$ أمريكي", "price_usd": 10.0}
}

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("💰 مستند حسابي ورصيدي")
    btn2 = types.KeyboardButton("🛒 تصفح الألعاب والخدمات")
    btn3 = types.KeyboardButton("➕ شحن رصيد (شام كاش)")
    btn4 = types.KeyboardButton("📞 الدعم الفني")
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    if user_id not in users_db:
        users_db[user_id] = {"balance_syr": 0, "docs_count": 0, "selected_product": None}
    bot.send_message(
        user_id, 
        f"🎯 أهلاً بك في متجر الشدات المطور والشحن الرقمي!\n"
        f"💵 سعر صرف المتجر: 1$ = {EXCHANGE_RATE:,} ل.س\n"
        f"⚡ رصيدك الحالي ومستنداتك آمنة ومحفوظة.", 
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda message: message.text == "💰 مستند حسابي ورصيدي")
def show_balance(message):
    user_id = message.chat.id
    if user_id not in users_db: users_db[user_id] = {"balance_syr": 0, "docs_count": 0, "selected_product": None}
    balance_syr = users_db[user_id]["balance_syr"]
    balance_usd = balance_syr / EXCHANGE_RATE if balance_syr > 0 else 0.0
    bot.send_message(
        user_id, 
        f"📋 **كشف حسابك المالي الحالي:**\n\n"
        f"💵 رصيدك بالليرة: {balance_syr:,} ل.س\n"
        f"💳 رصيدك بالدولار: {balance_usd:.2f} $\n"
        f"📄 مستندات الشراء المعتمدة: {users_db[user_id]['docs_count']}"
    )

@bot.message_handler(func=lambda message: message.text == "➕ شحن رصيد (شام كاش)")
def charge_request(message):
    bot.send_message(
        message.chat.id, 
        f"💳 **تعليمات الشحن عبر شام كاش (Sham Cash):**\n\n"
        f"يرجى تحويل قيمة الرصيد المطلوب إلى حساب محفظتنا التالي:\n"
        f"`{SHAM_CASH_WALLET}`\n\n"
        f"✍️ بعد إتمام عملية التحويل بنجاح، قم بإرسال قيمة المبلغ الذي قمت بتحويله **بالدولار ($)** هنا ليتم تقييده تلقائياً في حسابك بالليرة السورية:"
    )
    bot.register_next_step_handler(message, process_charging)

def process_charging(message):
    try:
        usd_amount = float(message.text)
        syr_amount = int(usd_amount * EXCHANGE_RATE)
        user_id = message.chat.id
        if user_id not in users_db: users_db[user_id] = {"balance_syr": 0, "docs_count": 0, "selected_product": None}
        users_db[user_id]["balance_syr"] += syr_amount
        bot.send_message(user_id, f"✅ تم استلام طلب الشحن وإضافة {syr_amount:,} ل.س لممحفظتك ما يعادل ({usd_amount}$).")
        bot.send_message(ADMIN_ID, f"💰 إشعار شحن مالي: قام آيدي ({user_id}) بإرسال طلب شحن بقيمة {usd_amount}$ وتم منح رصيد {syr_amount:,} ل.س")
    except ValueError:
        bot.send_message(message.chat.id, "❌ يرجى إدخال رقم صحيح فقط (مثال: 5 أو 10).")

@bot.message_handler(func=lambda message: message.text == "📞 الدعم الفني")
def support_info(message):
    bot.send_message(message.chat.id, f"📞 للتواصل مع الدعم الفني والإدارة للاستفسارات أو معالجة المشاكل المباشرة:\n\n💬 تيليجرام: [تواصل هنا](https://t.me{SUPPORT_NUMBER}) أو أرسل لمعرف الحساب مباشرة.")

@bot.message_handler(func=lambda message: message.text == "🛒 تصفح الألعاب والخدمات")
def show_categories(message):
    markup = types.InlineKeyboardMarkup()
    for key, name in CATEGORIES.items():
        markup.add(types.InlineKeyboardButton(name, callback_data=f"cat_{key}"))
    bot.send_message(message.chat.id, "🛒 اختر اللعبة أو الخدمة التي تريد تصفح باقاتها وأسعارها:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("cat_"))
def show_category_products(call):
    cat_key = call.data.split("_")[1]
    markup = types.InlineKeyboardMarkup()
    for p_key, item in PRODUCTS.items():
        if item["category"] == cat_key:
            price_syr = int(item["price_usd"] * EXCHANGE_RATE)
            markup.add(types.InlineKeyboardButton(f"{item['name']} - ({price_syr:,} ل.س)", callback_data=f"buy_{p_key}"))
    markup.add(types.InlineKeyboardButton("🔙 العودة للأقسام", callback_data="back_cats"))
    bot.edit_message_text("🛒 اختر الباقة المطلوبة للشراء الفوري:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "back_cats")
def back_to_categories(call):
    markup = types.InlineKeyboardMarkup()
    for key, name in CATEGORIES.items():
        markup.add(types.InlineKeyboardButton(name, callback_data=f"cat_{key}"))
    bot.edit_message_text("🛒 اختر اللعبة أو الخدمة التي تريد تصفح باقاتها وأسعارها:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def callback_buy(call):
    user_id = call.message.chat.id
    product_key = call.data.split("_")
    product_id = f"{product_key}_{product_key}"
    product = PRODUCTS[product_id]
    price_syr = int(product["price_usd"] * EXCHANGE_RATE)
    
    if user_id not in users_db: users_db[user_id] = {"balance_syr": 0, "docs_count": 0, "selected_product": None}
    
    if users_db[user_id]["balance_syr"] >= price_syr:
        users_db[user_id]["selected_product"] = product_id
        bot.send_message(user_id, f"🛒 لقد اخترت {product['name']}.\nمن فضلك أرسل الآن **آيدي (ID) اللاعب** الفعلي في اللعبة للشحن:")
        bot.register_next_step_handler(call.message, complete_purchase)
    else:
        bot.send_message(user_id, f"❌ رصيدك الحالي غير كافٍ. تحتاج إلى {price_syr:,} ل.س لشراء هذه الباقة.")

def complete_purchase(message):
    global orders_count
    user_id = message.chat.id
    game_id = message.text
    product_id = users_db[user_id]["selected_product"]
    
    if not product_id: return
    product = PRODUCTS[product_id]
    price_syr = int(product["price_usd"] * EXCHANGE_RATE)
    
    users_db[user_id]["balance_syr"] -= price_syr
    orders_count += 1
    
    pending_orders[orders_count] = {"user_id": user_id, "product_name": product["name"], "price": price_syr}
    users_db[user_id]["selected_product"] = None
    
    bot.send_message(user_id, f"✅ تم خصم الأموال وتوليد مستند الشراء `#{orders_count}`\n⏳ الطلب قيد المعالجة الفنية، سيقوم البوت بتسليمك كود الشحن فور صدوره من الإدارة.")
    
    # لوحة تحكم الأدمن الفورية للتحكم بالطلب من حساب التليجرام
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ إرسال الكود / تم الشحن", callback_data=f"sendcode_{orders_count}"))
    markup.add(types.InlineKeyboardButton("❌ رفض وإرجاع ليرات", callback_data=f"adminreject_{orders_count}"))
    
    bot.send_message(
        ADMIN_ID, 
        f"🚨 **مستند طلب شراء شدات جديد (#{orders_count})**\n\n"
        f"🆔 آيدي المشتري: `{user_id}`\n"
        f"🎮 **آيدي اللاعب المطلوب:** `{game_id}`\n"
        f"📦 الباقة المطلوبة: {product['name']}\n"
        f"💵 القيمة المستقطعة: {price_syr:,} ل.س\n\n"
        f"💡 اذهب للموزع واشحن للآيدي أو اشتر الكود، ثم اضغط على الزر أدناه لتأكيد العملية للزبون.",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def admin_actions(call):
    data_parts = call.data.split("_")
    action = data_parts
    order_id = int(data_parts)
    
    if order_id not in pending_orders:
        bot.answer_callback_query(call.id, "⚠️ هذا الطلب تم معالجته مسبقاً!")
        return

    order_data = pending_orders[order_id]
    customer_id = order_data["user_id"]
    
    if action == "sendcode":
        bot.answer_callback_query(call.id)
        bot.send_message(ADMIN_ID, f"✍ *طلب #{order_id}*:\nأرسل الآن كود الشحن أو عبارة تأكيد كرسالة نصية ليقوم البوت بتحويلها للزبون تلقائياً:")
        bot.register_next_step_handler(call.message, lambda msg: deliver_code(msg, order_id, customer_id))
        
    elif action == "adminreject":
        users_db[customer_id]["balance_syr"] += order_data["price"]
        bot.send_message(customer_id, f"❌ نعتذر منك، تم رفض طلبك رقم `#{order_id}` وإرجاع المبلغ المالي إلى محفظتك.")
