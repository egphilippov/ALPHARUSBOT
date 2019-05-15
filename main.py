import socket
import sys
import time
import requests
import settings
import translate_krzb
import whois

from urllib.parse import unquote

# Function shortening of ic.send.  
def send(mes):
  return irc.send(bytes(mes,'utf-8'))

# Function of parcing of get TITLE from link.  
def link_title(n):
    if 'http://' in n or 'https://' in n:
        try:
            link_r = n.split('//',1)[1].split(' ',1)[0].rstrip()
        except:
            print('Link wrong!')      
    elif 'www.' in n:
        try:
            link_r = n.split('www.',1)[1].split(' ',1)[0].rstrip()    
        except:
            print('Link wrong!')
    link = 'http://'+link_r        
    max_t_link = 30
    t_link = time.time()
    for i in requests.get(link, stream=True, verify=False):
        t2_link = time.time()
        if t2_link > t_link + max_t_link:
            requests.get(link, stream=True).close()
            print('Title - Ошибка! Превышено время ожидания!')
            link_stat = False
            break
        else:
            link_stat = True

    if link_stat == True:
        unquoted_link = unquote(link)
        get_title = requests.get(link, timeout = 10)
        txt_title = get_title.text
        if '</TITLE>' in txt_title or '</title>' in txt_title\
                      or '</Title>' in txt_title:
            if '</TITLE>' in txt_title:
                title = '\x02Title\x02 of '+n+': '+\
                txt_title.split('</TITLE>',1)[0].split('>')[-1]
            elif '</title>' in txt_title:
                title = '\x02Title\x02 of '+n+': '+\
                txt_title.split('</title>',1)[0].split('>')[-1]
            elif '</Title>' in txt_title:
                title = '\x02Title\x02 of '+n+': '+\
                txt_title.split('</Title>',1)[0].split('>')[-1]

            return title.replace('\r','').replace('\n','').replace\
                   ('www.','').replace('http://','').replace\
                   ('https://','').strip()
        else:
            return 'Title not found'
          
# Install min & max timer vote.  
min_timer = 30
max_timer = 300

network = settings.settings('network')
port = int(settings.settings('port'))
irc = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
channel = settings.settings('channel')
botName = settings.settings('botName')
masterName = settings.settings('masterName')
coinmarketcap_apikey = settings.settings('coinmarketcap_apikey')
titleEnabled = bool(settings.settings('titleEnabled'))
onlycmc = bool(settings.settings('onlycmc'))
enableother1 = not onlycmc

print("connecting...")
irc.connect ((network, port))
print("connected, sending login handshake")
#print (irc.recv(2048).decode("UTF-8"))
send('NICK '+botName+'\r\n')
send('USER '+botName+' '+botName+' '+botName+' :ircbot\r\n')
#send('NickServ IDENTIFY '+settings.settings('password')+'\r\n')
#send('MODE '+botName+' +x')

#-------Global_variables--------------------
   
name = ''
message = ''
message_voting = ''
voting_results = ''

count_voting = 0
count_vote_plus = 0
count_vote_minus = 0
count_vote_all = 0
while_count = 0

btc_usd = 0
eth_usd = 0
usd_rub = 0
eur_rub = 0
btc_rub = 0
btc_usd_old = 0
eth_usd_old = 0
usd_rub_old = 0
eur_rub_old = 0
btc_rub_old = 0
btc_usd_su = str('')
eth_usd_su = str('')
usd_rub_su = str('')
eur_rub_su = str('')
time_vote = 0

whois_ip = ''
whois_ip_get_text = ''

timer_exc = 0
time_exc = 0

where_mes_exc = ''
t2 = 0

#-------Massives----------------------------

dict_users = {}
dict_count = {}
dict_voted = {}
list_vote_ip = []

# List who free from anti-flood function.
list_floodfree = settings.settings('list_floodfree')
list_bot_not_work = settings.settings('list_bot_not_work')

while True:
    try:
        data = irc.recv(2048).decode("UTF-8")
    except:
        continue
    if data.find('PING') != -1:
        send('PONG '+data.split(" ")[1]+'\r\n')

    #001 welcome
    if data.split(" ")[1]=="001": send('JOIN '+channel+' \r\n')

    
    # Make variables Name, Message, IP from user message.
    if data.find('PRIVMSG') != -1:
        name = data.split('!',1)[0][1:]
        message = data.split('PRIVMSG',1)[1].split(':',1)[1]
    try:
        ip_user=data.split('@',1)[1].split(' ',1)[0]
    except:
        print('error getting ip_user')

    if enableother1:
        #-----------Translate_krzb---------    

        if 'PRIVMSG '+channel+' :!п ' in data \
           or 'PRIVMSG '+botName+' :!п ' in data:
            if 'PRIVMSG '+channel+' :!п ' in data:
                where_message = channel            
            elif 'PRIVMSG '+botName+' :!п ' in data:
                where_message = name
            
            tr_txt = message.split('!п ',1)[1].strip()
            res_txt = translate_krzb.tr(tr_txt)
            send('PRIVMSG '+where_message+' :\x02перевод с кракозябьечьего:\x02 '+res_txt+'\r\n')

    #-----------Bot_help---------------

    if 'PRIVMSG '+channel+' :!help' in data or 'PRIVMSG '+botName+' :!справка' in data or 'PRIVMSG '+botName+' :!помощь' in data or 'PRIVMSG '+botName+' :!хелп' in data:
        send('NOTICE %s : Помощь по командам бота:\r\n' %(name))
        send('NOTICE %s : ***Функция опроса: [!опрос (число) сек (тема опрос)], например\
(пишем без кавычек: \"!опрос 60 сек Вы любите ониме?\", если не писать время, то время\
установится на 60 сек\r\n' %(name))
        send('NOTICE %s : ***Функция курса: просто пишите (без кавычек): \"!курс\". Писать\
можно и в приват боту\r\n' %(name))
        send('NOTICE %s : ***Функция whois: что бы узнать расположение IP, просто пишите\
(без кавычек): \"!где айпи (IP)\", пример: \"!где айпи \
188.00.00.01\". Писать можно и в приват к боту\r\n' %(name))
        send('NOTICE %s : ***Функция перевода с английских букв на русские: \"!п tekst perevoda\", пример: \"!п ghbdtn\r\n' %(name))

    #-----------Anti_flood-------------

    # Count of while.  
    while_count += 1
    if while_count == 50:
        while_count = 0
        dict_count = {}
            
    # Insert nick in dict: dic_count.  
    if data.find('PRIVMSG') != -1 and name not in dict_count and\
       name not in list_floodfree:
        dict_count[name] = int(1)
        if 'PRIVMSG '+channel in data:
            where_message = channel
        elif 'PRIVMSG '+botName in data:
            where_message = botName
    
    # If new message as last message: count +1.  
    if data.find('PRIVMSG') != -1 and message == dict_users.get(name)\
       and name not in list_floodfree:
        dict_count[name] += int(1)
    
    # Add key and value in massiv.  
    if data.find('PRIVMSG') != -1 and name not in list_floodfree:
        dict_users[name] = message
    
    # Message about flood and kick. 
    #if data.find('PRIVMSG') != -1 and name not in list_floodfree:
    #    for key in dict_count: 
    #        if dict_count[key] == 3 and key != 'none':
    #            send('PRIVMSG '+where_message+' :'+key+', Прекрати флудить!\r\n')
    #            dict_count[key] += 1
    #        elif dict_count[key] > 5 and key != 'none':
    #            send('KICK '+channel+' '+key+' :Я же сказал не флуди!\r\n')
    #            dict_count[key] = 0
            
      
    # Out command.  
    if data.find('PRIVMSG '+channel+' :!quit') != -1 and name == masterName:
        send('PRIVMSG '+channel+' :Хорошо, всем счастливо оставаться!\r\n')
        send('QUIT\r\n')
        sys.exit()

    # Message per bot.  
    if "PRIVMSG %s :!напиши "%(channel) in data or\
       "PRIVMSG %s :!напиши "%(botName) in data and name == masterName:
        mes_per_bot = message.split('!напиши ',1)[1]
        send(mes_per_bot)
        
    #---------Whois servis--------------------------

    if enableother1:
      if 'PRIVMSG '+channel+' :!где айпи' in data\
       or 'PRIVMSG '+botName+' :!где айпи' in data:

        if 'PRIVMSG '+channel+' :!где айпи' in data:
            where_message_whois = channel
            
        elif 'PRIVMSG '+botName+' :!где айпи' in data:
            where_message_whois = name
                      
        try:
            whois_ip = data.split('!где айпи ',1)[1].split('\r',1)[0].strip()
            get_whois = whois.whois(whois_ip)
            country_whois = get_whois['country']
            city_whois = get_whois['city']
            address_whois = get_whois['address']    
            print(get_whois)

            if country_whois == None:
                country_whois = 'None'
            if city_whois == None:
                city_whois = 'None'
            if address_whois == None:
                address_whois = 'None'    
                       
            whois_final_reply = ' \x02IP:\x02 '+whois_ip+' \x02Страна:\x02 '+\
            country_whois+' \x02Адресс:\x02 '+address_whois+'\r\n'
            send('PRIVMSG '+where_message_whois+' :'+whois_final_reply)            

        except:
            print('get Value Error in whois servis!')
            send('PRIVMSG '+where_message_whois+' :Ошибка! Вводите только IP адрес \
из цифр, разделенных точками!\r\n')
                     
    #---------Info from link in channel-------------
    
    if enableother1 and titleEnabled:
        if 'PRIVMSG %s :'%(channel) in data and '.png' not in data and '.jpg' not in data and '.doc'\
        not in data and 'tiff' not in data and 'gif' not in data and '.jpeg' not in data and '.pdf' not in data:
            if 'http://' in data or 'https://' in data or 'www.' in data:
                try:
                   send('PRIVMSG %s :%s\r\n'%(channel,link_title(data)))
                except requests.exceptions.ConnectionError:
                    print('Ошибка получения Title (requests.exceptions.ConnectionError)')
                    send('PRIVMSG '+channel+' :Ошибка, возможно такого адреса нет\r\n')
                except:
                    print('Error link!')  
    #---------Voting--------------------------------
                
    t = time.time()
    if enableother1:
      if '!стоп опрос' in data and 'PRIVMSG' in data and name == masterName:
        t2 = 0
        print('счетчик опроса сброшен хозяином!')
    if enableother1:
      if 'PRIVMSG '+channel+' :!опрос ' in data and ip_user not in list_bot_not_work:
        if t2 == 0 or t > t2+time_vote:
            if ' сек ' not in data:
                time_vote = 60
                # Make variable - text-voting-title form massage.  
                message_voting = message.split('!опрос',1)[1].strip()
            if ' сек ' in data:
                try:
                    # Get time of timer from user message.  
                    time_vote = int(message.split('!опрос',1)[1].split('сек',1)[0].strip())
                    # Make variable - text-voting-title form massage.  
                    message_voting = message.split('!опрос',1)[1].split('сек',1)[1].strip()
                except:
                    time_vote = 60
                    # Make variable - text-voting-title form massage.  
                    message_voting = message.split('!опрос',1)[1].strip()

            if min_timer>time_vote or max_timer<time_vote:
                send('PRIVMSG %s :Ошибка ввода таймера голосования.\
Введите от %s до %s сек!\r\n'%(channel,min_timer,max_timer))
                continue
            
            t2 = time.time()
            count_vote_plus = 0
            count_vote_minus = 0
            vote_all = 0
            count_voting = 0
            list_vote_ip = []
            # Do null voting massiv.  
            dict_voted = {}
            send('PRIVMSG %s :Начинается опрос: \"%s\". Опрос будет идти \
%d секунд. Чтобы ответить "да", пишите: \"!да\" \
", чтобы ответить "нет", пишите: \"!нет\". Писать можно как открыто в канал,\
так и в приват боту, чтобы голосовать анонимно \r\n' % (channel,message_voting,time_vote))
            list_vote_ip = []
                
    # If find '!да' count +1.  
    if enableother1:
      if data.find('PRIVMSG '+channel+' :!да') != -1 or data.find('PRIVMSG '+botName+' :!да') != -1:
        if ip_user not in list_vote_ip and t2 != 0:
            count_vote_plus +=1
            dict_voted[name] = 'yes'
            list_vote_ip.append(ip_user)
            # Make notice massage to votes user.  
            send('NOTICE '+name+' :Ваш ответ \"да\" учтен!\r\n')

    # If find '!нет' count +1.  
    if enableother1:
      if data.find('PRIVMSG '+channel+' :!нет') != -1 or data.find('PRIVMSG '+botName+' :!нет') != -1:
        if ip_user not in list_vote_ip and t2 != 0:
            count_vote_minus +=1
            dict_voted[name] = 'no'
            list_vote_ip.append(ip_user)
            # Make notice massage to votes user.  
            send('NOTICE '+name+' :Ваш ответ \"нет\" учтен!\r\n')
   
    # If masterName send '!список голосования': send to him privat messag with dictonary Who How voted.  
    if enableother1:
      if data.find('PRIVMSG '+botName+' :!список опроса') !=-1 and name == masterName:
        for i in dict_voted:
            send('PRIVMSG '+masterName+' : '+i+': '+dict_voted[i]+'\r\n')

    # Count how much was message in channel '!голосование'.  
    if enableother1:
      if data.find('PRIVMSG '+channel+' :!опрос') != -1 and t2 != 0:
        count_voting += 1

    # If voting is not end, and users send '!голосование...': send message in channel.  
    t4 = time.time()
    if enableother1:
      if data.find('PRIVMSG '+channel+' :!опрос') != -1 and t4-t2 > 5:
        t3 = time.time()
        time_vote_rest_min = (time_vote-(t3-t2))//60
        time_vote_rest_sec = (time_vote-(t3-t2))%60
        if (time_vote-(t3-t2)) > 0:
            send('PRIVMSG %s : Предыдущий опрос: \"%s\" ещё не окончен, до окончания \
опроса осталось: %d мин %d сек\r\n \
' % (channel,message_voting,time_vote_rest_min,time_vote_rest_sec))

    # Make variable message rusults voting.  
    vote_all = count_vote_minus + count_vote_plus
    voting_results = 'PRIVMSG %s : результаты опроса: \"%s\", "Да" ответило: %d \
человек(а), "Нет" ответило: %d человек(а), Всего ответило: %d человек(а) \
\r\n' % (channel, message_voting, count_vote_plus, count_vote_minus, vote_all)

    # When voting End: send to channel ruselts and time count to zero.  
    if t-t2 > time_vote and t2 != 0:
        t2 = 0
        send('PRIVMSG '+channel+' : Опрос окончен!\r\n')
        send(voting_results)
    
    if 'PRIVMSG '+channel+' :!курс' in data or 'PRIVMSG '+botName+' :!курс' in data:
        if 'PRIVMSG '+channel+' :!курс' in data:
            where_mes_exc = channel
        if 'PRIVMSG '+botName+' :!курс' in data:
            where_mes_exc = name

        try:
            #This example uses Python 2.7 and the python-request library.
            
            from requests import Request, Session
            from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
            import json
            
            url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
            parameters = {
              'symbol':'BTC,ETH',
              'convert':'USD'
            }
            headers = {
              'Accepts': 'application/json',
              'X-CMC_PRO_API_KEY': coinmarketcap_apikey,
            }
            
            session = Session()
            session.headers.update(headers)
            
            try:
              response = session.get(url, params=parameters)
              cmc = json.loads(response.text)
              print(cmc)
            except (ConnectionError, Timeout, TooManyRedirects) as e:
              print(e)
        except:
            print('Исключение api cmc: ?')
        btc_usd = cmc["data"]["BTC"]["quote"]["USD"]["price"]
        eth_usd = cmc["data"]["ETH"]["quote"]["USD"]["price"]


        btc_usd_str = str(btc_usd)
        eth_usd_str = str(eth_usd)

        send_res_exc = '\x033Курс CoinMarketCap: \x02BTC/USD:\x02 '+btc_usd_str+' \x02ETH/USD:\x02 '+eth_usd_str+'\r\n'

        send('PRIVMSG %s :%s\r\n'%(where_mes_exc,send_res_exc))
    
    #------------Printing---------------

    print(data)
