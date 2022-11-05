
 # DATE: [MessageHandler(
                # Filters.regex(
                    # '^([0-9]{1,2}\\.[0-9]{1,2}\\.[0-9]{4}|Сегодня|Текущий месяц|[0-9]{1,2}\\.[0-9]{4})$'
                # ),
                # find_rate)]        
        
### regex для поиска сообщения о выбранной валюте
        # states={
            # CURRENCY: [MessageHandler(
            #     Filters.regex(
            #         '^(USD|EUR|CHF|RUB|Все валюты)$'
            #     ),
            #     pick_date)],
            
            
        # перебрать тут циклом?
        # if (update.message['text'] == 'USD'
        #    or update.message['text'] == 'EUR'
        #    or update.message['text'] == 'CHF'
        #    or update.message['text'] == 'RUB'):
        #     msg = update.message['text']
        #     currency = [update.message['text']]
        #     logger.info(f'{msg} ---- {currency}')
        # elif update.message['text'] == 'Все валюты':
        #     currency = ALL_CURRENCIES_LIST
        
        
        
        
        # def currency_pick(update: Update, context: ContextTypes):
#     chat = update.effective_chat
#     button = ReplyKeyboardMarkup(keyboard=CURRENCU_MENU,
#                                  resize_keyboard=True)

#     global func_name
#     func_name = update['message']['text']

#     context.bot.send_message(
#         chat_id=chat.id,
#         reply_markup=button,
#         text=('Выбери из предложенных валют')
#     )
#     # logger.info(CURRENCY, '<- вернули')
#     return CURRENCY


# def find_rate(update: Update, context: ContextTypes):
#     currency = ALL_CURRENCIES_LIST
#     global func_name
#     try:
#         button = ReplyKeyboardMarkup(keyboard=MAIN_MENU_KEYBOARD,
#                                      resize_keyboard=True)
#         chat = update.effective_chat
#         date_rate = ''
        
#         if func_name == '/rate_on_date':
#             caller = 'rate_on_date'
#             if update.message['text'] == 'Сегодня':
#                 date_rate = date.today().strftime('%d.%m.%Y')
#             else:
#                 date_rate = update.message['text']
        
#         if func_name == '/rate_for_month':
#             caller = 'rate_for_month'
#             if update.message['text'] == 'Текущий месяц':
#                 date_rate = date.today().strftime('%m.%Y')
#             else:
#                 date_rate = update.message['text']

#         if update.message['text'] == '/rate_year_to_date':
#             func_name = '/rate_year_to_date'
#             caller = 'rate_year_to_date'

#         logger.info(f'call find_rate with args:'
#                     f'{date_rate}, {currency}, {caller}')
        
#         logger.info(f'call res: {(date_rate, currency, caller)}')
#         res = get_rate(date_rate, currency, caller)
#         logger.info(f'called res {res}')
#         # очищаем ответ от всех символов, кроме указанных в первом аргументе re.sub
#         res_msg = re.sub('[^A-Za-z0-9|А-Яа-я|.|:| ]+', '', json.dumps(res[0]))
#         date_start = res[1]
#         date_end = res[2]
        
#         if date_start == date_end:
#             text = f'Курсы на {res[1]}\r\n \r\n{res_msg}'
#         else:
#             text = f'Курсы с {res[1]} по {res[2]}\r\n \r\n{res_msg}'

#         context.bot.send_message(
#             chat_id=chat.id,
#             reply_markup=button,
#             text=text
#         )
#         return ConversationHandler.END
#     except Exception as er:
#         logger.error(er)


# def pick_date(update: Update, context: ContextTypes):
#     """ """
#     logger.info('we are in the pick_date function')
#     global currency
#     global func_name
#     buttons: list = []
#     text: list = []
#     func_name = update['message']['text']

#     try:
#         if func_name == '/rate_on_date':
            
#             text = 'Введи дату в формате 01.01.2022'
#             buttons = ['Сегодня']
#         elif func_name == '/rate_for_month':
#             text = 'Введи месяц и год в формате 10.2022'
#             buttons = ['Текущий месяц']

#         logger.info(f'func name - {func_name}, buttons - {buttons}'
#                     f'{text}')
#         context.bot.send_message(
#             chat_id=update.effective_chat.id,
#             text=text,
#             reply_markup=telegramcalendar.create_calendar(),
#         )
#         return DATE
#     except Exception as er:
#         logger.error(f'{er}')