import asyncio
import aioschedule
from telebot.async_telebot import AsyncTeleBot
import process_data_base

from telebot import asyncio_helper

API_TOKEN = '' #insert your token
bot = AsyncTeleBot(API_TOKEN)


@bot.message_handler(commands=['start'])
async def send_welcome(message):
    await bot.reply_to(message, "Hi! Use /start_game <nickname> to start a game. To finish game use /finish_game")


@bot.message_handler(commands=['help'])
async def send_welcome(message):
    await bot.reply_to(message, "Use /trade to trade."
                                "Use /stats to see information about yourself. "
                                "Use /travel to see possible destinations."
                                "Use /finish_game to finish game")


@bot.message_handler(commands=['start_game'])
async def start_game(message):
    args = message.text.split()
    if len(args) > 1:
        nickname = str(args[1])
        process_data_base.create_user(nickname, message.chat.id)
        await bot.reply_to(message, "You are in MartsirtTown. It's hospitable and safe place. Use /trade to trade."
                                    " Use /stats to see information about yourself. "
                                    "Use /travel to see possible destinations."
                                    "Use /finish_game to finish game")
    else:
        await bot.reply_to(message, 'Use /start_game <nickname> to start a game')


@bot.message_handler(commands=['finish_game'])
async def finish_game(message):
    process_data_base.finish_game(message.chat.id)
    await bot.reply_to(message, "Game finished")


@bot.message_handler(commands=['stats'])
async def stats(message):
    if process_data_base.check_user(message.chat.id):
        info = process_data_base.stats(message.chat.id)
        await bot.reply_to(message, info)
    else:
        await bot.reply_to(message, "Firstly start game ")


@bot.message_handler(commands=['trade'])
async def trade(message):
    if process_data_base.check_user(message.from_user.id):
        if process_data_base.check_trade_possibility(message.from_user.id):
            await bot.reply_to(message, "Use /stats to explore your inventory. Use /sell <item_name> to sell. "
                                        "Use /buy <item_name> to buy. Possible items to buy or sell: 1)Steel_Sword 2)Holy_Sword 3)Heal_Poison"
                                        "4)Mana_Poison 5)Leather_Armor 6)Armour_of_magic_resistance")
        else:
            await bot.reply_to(message, "You are not in the safe place. Go to the nearest town")
    else:
        await bot.reply_to(message, "Firstly start game ")


@bot.message_handler(commands=['sell'])
async def sell(message):
    if process_data_base.check_user(message.from_user.id):
        if process_data_base.check_trade_possibility(message.from_user.id):
            arg = message.text.split()
            if 1 < len(arg) < 3:
                if process_data_base.sell_item(str(arg[1]), message.from_user.id):
                    await bot.reply_to(message, "Done")
                else:
                    await bot.reply_to(message, "There are no items with this name in the inventory")
            else:
                await bot.reply_to(message, "Incorrect params. Use /sell <item_name>")
        else:
            await bot.reply_to(message, "You are not in the safe place. Go to the nearest town")
    else:
        await bot.reply_to(message, "Firstly start game ")


@bot.message_handler(commands=['buy'])
async def buy(message):
    if process_data_base.check_user(message.from_user.id):
        if process_data_base.check_trade_possibility(message.from_user.id):
            arg = message.text.split()
            if 1 < len(arg) < 3:
                if process_data_base.buy_item(str(arg[1]), message.from_user.id):
                    await bot.reply_to(message, "Done")
                else:
                    await bot.reply_to(message, "There are no items with this name in the shop or your have not enough money")
            else:
                await bot.reply_to(message, "Incorrect params. Use /buy <item_name>")
        else:
            await bot.reply_to(message, "You are not in the safe place. Go to the nearest town")
    else:
        await bot.reply_to(message, "Firstly start game ")


@bot.message_handler(commands=['travel'])
async def travel(message):
    if process_data_base.check_user(message.from_user.id):
        describe = process_data_base.travel(message.from_user.id)
        if describe == 0:
            await bot.reply_to(message, "You cant' travel because you are in battle")
        else:
            ans = "You are in " + describe + ". Use /travel_to <location_name> to travel. " \
                                             "Locations: " \
                                             "1)Martsirt_Town " \
                                             "2)Rogue_Camp" \
                                             "3)Deadly_Swamp"
            await bot.reply_to(message, ans)
    else:
        await bot.reply_to(message, "Firstly start game")


@bot.message_handler(commands=['travel_to'])
async def travel_to(message):
    if process_data_base.check_user(message.from_user.id):
        arg = message.text.split()
        if 1 < len(arg) < 3:
            location_name = arg[1]
            if location_name != "Martsirt_Town" and location_name != "Rogue_Camp" and location_name != "Deadly_Swamp":
                await bot.reply_to(message, "Incorrect location name")
            else:
                describe = process_data_base.travel(message.from_user.id)
                if describe == 0:
                    await bot.reply_to(message, "You cant' travel because you are in battle")
                else:
                    response = process_data_base.travel_to(location_name, message.from_user.id)
                    if response == 0:
                        await bot.reply_to(message, "Your are in town")
                    else:
                        await bot.reply_to(message, "Your are in the dungeon, prepare to fight. Use /attack")
        else:
            await bot.reply_to(message, "Incorrect params")
    else:
        await bot.reply_to(message, "Firstly start game")


@bot.message_handler(commands=['attack'])
async def attack(message):
    if process_data_base.check_user(message.from_user.id):
        describe = process_data_base.travel(message.from_user.id)
        print(describe)
        if describe != 0:
            await bot.reply_to(message, "No enemies to attack")
        else:
            info = process_data_base.enemy_stats(message.from_user.id)
            info = "info about enemy " + info + "use /attack_mob to proceed battle iteration. " \
                                                "Weapon and armour would be chosen automatically with the best profit for you" \
                                                "use /use_mana_poison to use mana poison" \
                                                "use /use_heal_poison to use heal poison"
            await bot.reply_to(message, info)
    else:
        await bot.reply_to(message, "Firstly start game")


@bot.message_handler(commands=['attack_mob'])
async def attack_mob(message):
    if process_data_base.check_user(message.from_user.id):
        describe = process_data_base.travel(message.from_user.id)
        if describe != 0:
            await bot.reply_to(message, "No enemies to attack")
        else:
            response = process_data_base.attack_mob(message.from_user.id)
            if response == 1:
                await bot.reply_to(message, "You killed enemy")
            else:
                response = process_data_base.mob_attack_you(message.from_user.id)
                if response == 0:
                    process_data_base.finish_game(message.from_user.id)
                    await bot.reply_to(message, "You are killed ):")
                else:
                    await bot.reply_to(message, "Round is finished")
    else:
        await bot.reply_to(message, "Firstly start game")


@bot.message_handler(commands=['use_mana_poison'])
async def use_mana(message):
    if process_data_base.check_user(message.from_user.id):
        response = process_data_base.use_mana_poison(message.from_user.id)
        if response == 0:
            await bot.reply_to(message, "You have no mana poisons")
        else:
            await bot.reply_to(message, "Done")
    else:
        await bot.reply_to(message, "Firstly start game")


@bot.message_handler(commands=['use_heal_poison'])
async def use_heal(message):
    if process_data_base.check_user(message.from_user.id):
        response = process_data_base.use_heal_poison(message.from_user.id)
        if response == 0:
            await bot.reply_to(message, "You have no heal poisons")
        else:
            await bot.reply_to(message, "Done")
    else:
        await bot.reply_to(message, "Firstly start game")

async def scheduler():
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def main():
    await asyncio.gather(bot.infinity_polling(), scheduler())


if __name__ == '__main__':
    asyncio.run(main())
