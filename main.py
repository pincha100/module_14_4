from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from crud_functions import initiate_db, get_all_products, add_products

API_TOKEN = ""
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Главная клавиатура с кнопками
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(KeyboardButton("Купить"), KeyboardButton("Информация"), KeyboardButton("Рассчитать"))

# Inline меню для расчёта
calc_menu = InlineKeyboardMarkup(row_width=2)
calc_menu.add(
    InlineKeyboardButton("Рассчитать норму калорий", callback_data="calories"),
    InlineKeyboardButton("Формулы расчёта", callback_data="formulas")
)


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Добро пожаловать! Выберите действие из меню:", reply_markup=main_menu)


@dp.message_handler(text="Купить")
async def get_buying_list(message: types.Message):
    """Отправляет список продуктов из базы данных."""
    products = get_all_products()
    if not products:
        await message.answer("Нет доступных продуктов для покупки.")
        return

    buying_menu = InlineKeyboardMarkup(row_width=2)
    for product in products:
        product_id, title, description, price = product
        await message.answer_photo(
            photo=f"https://via.placeholder.com/150?text={title}",
            caption=f"Название: {title} | Описание: {description} | Цена: {price} руб."
        )
        buying_menu.add(InlineKeyboardButton(f"Купить {title}", callback_data=f"buy_{product_id}"))

    await message.answer("Выберите продукт для покупки:", reply_markup=buying_menu)


@dp.callback_query_handler(lambda call: call.data.startswith("buy_"))
async def send_confirm_message(call: types.CallbackQuery):
    """Обрабатывает покупку продукта."""
    product_id = call.data.split("_")[1]
    await call.message.answer(f"Вы успешно приобрели продукт с ID {product_id}!")
    await call.answer()


@dp.message_handler(text="Рассчитать")
async def calculate_menu(message: types.Message):
    """Отправляет меню для расчёта калорий."""
    await message.answer("Выберите опцию:", reply_markup=calc_menu)


@dp.callback_query_handler(text="calories")
async def calculate_calories(call: types.CallbackQuery):
    """Запрашивает ввод данных для расчёта калорий."""
    await call.message.answer("Введите ваш возраст:")
    await call.answer()


@dp.callback_query_handler(text="formulas")
async def show_formulas(call: types.CallbackQuery):
    """Отправляет формулы расчёта калорий."""
    formula = (
        "Формула Миффлина-Сан Жеора:\n"
        "Мужчины: 10 × вес (кг) + 6.25 × рост (см) − 5 × возраст (лет) + 5\n"
        "Женщины: 10 × вес (кг) + 6.25 × рост (см) − 5 × возраст (лет) − 161"
    )
    await call.message.answer(formula)
    await call.answer()


if __name__ == "__main__":
    initiate_db()
    add_products()
    executor.start_polling(dp, skip_updates=True)
