        
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
