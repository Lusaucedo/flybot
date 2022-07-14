import os
import telebot
import requests
from datetime import datetime, timedelta

# API_KEY = os.getenv('API_KEY')
API_KEY = '5190288499:AAEsXUOyOgl6Al6eTQVsaTiS87_fynHeEeI'
bot = telebot.TeleBot(API_KEY)
chats = {}


def get_flight_number(input):
    # DEVUELVE EL DATO O NULL
    splitted = input.split()
    if (len(splitted) < 2):
        return None
    else: 
        return splitted[1]
    
 
def date_format(date_time):
    # DEVUELVE LA FECHA EN FORMATO DD/MM/YYYY
    #Se espera la fecha en el sig formato: 2022-05-26T06:20:00+00:00
    date_time = date_time.split('T') 
    day = '/'.join(reversed(date_time[0].split('-')))
    time = date_time[1].split('+')[0][:5] # Se separa en 2 partes y se queda con la primera    
    return f'{day} a las {time} hs'


def translate_status(status):
    return {
        'scheduled': 'Programado',
        'active': 'Activo',
        'landed': 'Aterrizado',
        'cancelled': 'Cancelado',
        'incident': 'Incidente',
        'diverted': 'Desviado'
    } [status]
    

def get_flight_info(flight_number):
    params = {
    'access_key': '059fa415a34581bff2a5dd7b9b75d954',
    'flight_iata': flight_number
    }

    api_result = requests.get('http://api.aviationstack.com/v1/flights', params)

    api_response = api_result.json()
    if not api_response['data']:
        return ('Mmm...\U0001F914\n\nParece que el número de vuelo ingresado no existe. \n\nRevisá que lo hayas escrito bien, y luego intentá nuevamente.')

    information = ''
    for flight in api_response['data']:
        departure = flight['departure']
        arrival = flight['arrival']

        information = f'''INFORMACIÓN DEL VUELO {flight_number} \u2708\uFE0F\n
    - Estado: {translate_status(flight['flight_status'])}\n   
    - Aeropuerto salida: {departure['airport']}
    - Terminal salida: {departure['terminal'] if departure['terminal'] != None else '-'}
    - Estima: { date_format(departure['estimated']) if departure['estimated'] != None else '-' }
    - Demora: {str(departure['delay']) + ' min' if departure['delay'] != None else '-'}
    - Actual: { date_format(departure['actual']) if departure['actual'] != None else '-' }\n
    - Aeropuerto llegada: {arrival['airport']}
    - Terminal llegada: {arrival['terminal'] if arrival['terminal'] != None else '-'}
    - Estima: { date_format(arrival['estimated']) if arrival['estimated'] != None else '-' }
    - Demora: {str(arrival['delay']) + ' min' if arrival['delay'] != None else '-'}
    - Actual: { date_format(arrival['actual']) if arrival['actual'] != None else '-' }'''

    return information


def send(chat_id, text, parse_mode = None):
    bot.send_message(chat_id, text, parse_mode)


def welcome(message):
    return send(message.chat.id, f'Hola {message.from_user.first_name}! \U0001F60A \n\nSoy *FlyBot* y puedo ayudarte a conocer el estado de un vuelo. \n\nSolo necesito que escribas el comando \'/vuelo\' + el número del mismo, por ejemplo : /vuelo AA1234.', 'Markdown')


@bot.message_handler(commands=['vuelo'])
def flights(message):
    flight_number = get_flight_number(message.text)
    
    if flight_number is None:
        return send(message.chat.id, '\u2049\uFE0F Falta el número de vuelo. Ejemplo: /vuelo AA1234')

    if len(flight_number) != 6:
        return send(message.chat.id, 'Lo siento, el número de vuelo ingresado tiene un formato inválido \U0001F605 \n\nRevisá que lo hayas escrito bien, y luego intentá nuevamente.')
                   
    flight_info = get_flight_info(flight_number)
    return send(message.chat.id, flight_info)
    

@bot.message_handler(func=lambda m: True)
def process_message(message):
    user_id = message.from_user.id
    
    if user_id in chats:
        ## existe el chat con ese user
        last_message = chats[user_id]
        limit_time = datetime.now() - timedelta(hours=1)
        
        chats[user_id] = datetime.now()
        
        if limit_time > last_message:
            welcome(message)
        else:
            return send(message.chat.id, f'Oops! \U0001F613 \n\nCreo que no te entendí, intentemos nuevamente.\n\nRecordá escribir \' /vuelo \' + el número de vuelo correspondiente. Por ejemplo: /vuelo AA1234.')
    else:
        ## no existe
        chats[user_id] = datetime.now()
        welcome(message)

bot.polling(non_stop=True)
