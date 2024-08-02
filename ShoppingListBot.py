import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получение токена из переменной окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# Обработчик команды /start с кнопками
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        ["Добавить товар", "Удалить товар"],
        ["Показать список", "Очистить список"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text('Выберите действие:', reply_markup=reply_markup)

# Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    logger.info(f"Received message: {text}")
    if text == "Добавить товар":
        await update.message.reply_text("Введите название товара для добавления:")
        context.user_data['state'] = 'add_item'
    elif text == "Удалить товар":
        shopping_list = context.user_data.get('shopping_list', [])
        if shopping_list:
            items = '\n'.join(f"{i+1}. {item}" for i, item in enumerate(shopping_list))
            await update.message.reply_text(f"Выберите номер товара для удаления:\n{items}")
            context.user_data['state'] = 'delete_item'
        else:
            await update.message.reply_text("Список покупок пуст.")
    elif text == "Показать список":
        await list_items(update, context)
    elif text == "Очистить список":
        await clear_list(update, context)
    elif context.user_data.get('state') == 'add_item':
        await add_item(update, context)
    elif context.user_data.get('state') == 'delete_item':
        await delete_item(update, context)

# Обработчик добавления товара
async def add_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    logger.info(f"Adding item: {user_message}")
    context.user_data['shopping_list'] = context.user_data.get('shopping_list', [])
    context.user_data['shopping_list'].append(user_message)
    await update.message.reply_text(f'Товар "{user_message}" добавлен в список покупок.')
    context.user_data['state'] = None

# Обработчик удаления товара
async def delete_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    try:
        item_index = int(user_message) - 1
        shopping_list = context.user_data.get('shopping_list', [])
        if 0 <= item_index < len(shopping_list):
            deleted_item = shopping_list.pop(item_index)
            await update.message.reply_text(f'Товар "{deleted_item}" удален из списка покупок.')
        else:
            await update.message.reply_text('Неверный номер товара.')
    except ValueError:
        await update.message.reply_text('Пожалуйста, введите номер товара.')
    context.user_data['state'] = None

# Обработчик команды /list
async def list_items(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    shopping_list = context.user_data.get('shopping_list', [])
    if shopping_list:
        items = '\n'.join(shopping_list)
        await update.message.reply_text(f'Список покупок:\n{items}')
    else:
        await update.message.reply_text('Список покупок пуст.')

# Обработчик команды /clear
async def clear_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['shopping_list'] = []
    await update.message.reply_text('Список покупок очищен.')

# Обработчик команды /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "/start - Начать работу с ботом\n"
        "/add - Добавить товар в список покупок\n"
        "/list - Показать текущий список покупок\n"
        "/clear - Очистить список покупок\n"
        "/help - Показать это сообщение"
    )
    await update.message.reply_text(help_text)

# Добавление обработчиков в приложение
def main() -> None:
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CommandHandler("help", help_command))

    application.run_polling()

if __name__ == '__main__':
    main()