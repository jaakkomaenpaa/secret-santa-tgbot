import os
from dotenv import load_dotenv
import random

from telegram import Update, ForceReply, Bot
from telegram.ext import filters, MessageHandler, Application, CommandHandler, ContextTypes

load_dotenv()
BOT_TOKEN = os.environ.get("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello! Please add me to a group before use.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        """
        Add this bot to a group, where everyone who wants to participate in the secret
        santa activity is an administrator. 
        Then, give the command draw_names and 
        everyone participating will receive the username of their target as a private
        message. 
        Everyone should also have had at least one message with this bot 
        before initiating the draw.
        """
    )


async def draw_names(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    This needs to be used in a group where everyone participating into the draw
    is an admin
    """

    chat_id = update.message.chat_id
    try:
        member_objects = await context.bot.get_chat_administrators(chat_id)
    except Exception as e:
        print(f"Error: {e}")
        return

    usernames = []
    for member in member_objects:
        usernames.append(member.user.username)

    name_dict = make_draw(usernames)

    for member in member_objects:
        print(member.user)
        try:
            await context.bot.send_message(chat_id=member.user.id, text=f"@{name_dict[member.user.username]}")
        except Exception as e:
            print(f"Error: {e}")


def make_draw(usernames):

    name_dict = {}
    members_available = usernames[:]

    for current_user in usernames:

        # Assign last two users manually
        if len(members_available) == 2:

            last_user = usernames[-1]

            if current_user != members_available[0] and last_user != members_available[1]:
                name_dict[last_user] = members_available[1]
                name_dict[current_user] = members_available[0]
            else:
                name_dict[last_user] = members_available[0]
                name_dict[current_user] = members_available[1]
            break

        names_not_own = [name for name in members_available if name != current_user]

        if not names_not_own:
            break

        random_name = random.sample(names_not_own, 1)[0]
        name_dict[current_user] = random_name
        members_available.remove(random_name)

    return name_dict


def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("draw_names", draw_names))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
