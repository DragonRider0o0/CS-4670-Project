import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.httpclient import AsyncHTTPClient
import json
#import urllib2
import httplib


#gameEngine = None
database = None
webSocketClients = []
mongoClient = None
webSocketIndex = 0
http_client = None
source = "Game Engine"
server = {
    'ip': "127.0.0.1",
    'port': '5500'
}


def main(port=6500):
    global database
    database = Database()
    global gameEngine
    gameEngine = GameEngine(port)


class Database:
    name = "GameEngine"
    httpClients = "HTTPClients"
    serverSessions = "ServerSessions"
    gameSessions = "GameSessions"
    players = "Players"
    game = "Game"
    gameUpdates = "GameUpdates"
    gameInformation = "GameInformation"
    chatMessages = "ChatMessages"
    database = None
    game_session_count = 0

    def __init__(self):
        global mongoClient
        from pymongo import MongoClient

        mongoClient = MongoClient()
        self.database = mongoClient[self.name]

    def add_http_client(self, http_client):
        http_clients = self.get_http_clients()
        for http_client_item in http_clients:
            if http_client_item['Ip'] == http_client['Ip'] and http_client_item['Port'] == http_client['Port']:
                return
            else:
                pass
        collection = self.database[self.httpClients]
        document = {'HTTPClient': http_client}
        collection.insert(document)

    def get_http_clients(self):
        collection = self.database[self.httpClients]
        documents = collection.find()
        if documents is None:
            return None
        http_clients = []
        for document in documents:
            http_clients.append(document['HTTPClient'])
        return http_clients

    def add_server_session(self, server_session):
        collection = self.database[self.serverSessions]
        session_number = server_session['SessionNumber']
        server_session_item = self.get_server_session(session_number)
        if server_session_item is None:
            document = {'Session': server_session, 'SessionNumber': session_number}
            collection.insert(document)
        else:
            database.remove_session(session_number)
            document = {'Session': server_session, 'SessionNumber': session_number}
            collection.insert(document)

    def get_server_session(self, server_session_number):
        collection = self.database[self.serverSessions]
        document = collection.find_one({"SessionNumber": server_session_number})
        if document is None:
            return None
        server_session = document['Session']
        return server_session

    def remove_server_session(self, server_session_number):
        collection = self.database[self.serverSessions]
        document = collection.find_one({"SessionNumber": server_session_number})
        if document is None:
            return False
        else:
            collection.remove({'Session': server_session_number})
            return True

    def add_game_session(self, game_session):
        collection = self.database[self.gameSessions]
        game_session_number = game_session['SessionNumber']
        game_session_item = self.get_game_session(game_session_number)
        if game_session_item is None:
            self.game_session_count += 1
            game_session['SessionNumber'] = self.game_session_count
            document = {'Session': game_session, 'SessionNumber': self.game_session_count}
            collection.insert(document)
            return self.game_session_count
        else:
            if game_session_item["PlayerName"] == game_session["PlayerName"]:
                return game_session_number
            else:
                self.game_session_count += 1
                game_session['SessionNumber'] = self.game_session_count
                document = {'Session': game_session, 'SessionNumber': self.game_session_count}
                collection.insert(document)
                return self.game_session_count

    def get_game_session(self, game_session_number):
        collection = self.database[self.gameSessions]
        document = collection.find_one({"SessionNumber": game_session_number})
        if document is None:
            return None
        game_session = document['Session']
        return game_session

    def remove_game_session(self, game_session_number):
        collection = self.database[self.gameSessions]
        document = collection.find_one({"SessionNumber": game_session_number})
        if document is None:
            return False
        else:
            collection.remove({'Session': game_session_number})
            return True

    def add_player(self, player):
        collection = self.database[self.players]
        player_name = player['PlayerName']
        player_item = self.get_player(player_name)
        if player_item is None:
            pass
        else:
            self.remove_player(player_name)
        document = {'Player': player, 'PlayerName': player_name}
        collection.insert(document)

    def get_player(self, player_name):
        collection = self.database[self.players]
        document = collection.find_one({"PlayerName": player_name})
        if document is None:
            return None
        player = document['Player']
        return player

    def remove_player(self, player_name):
        collection = self.database[self.users]
        document = collection.find_one({"Player": player_name})
        if document is None:
            return False
        else:
            collection.remove({'Player': player_name})
            return True

    def set_game(self, game):
        collection = self.database[self.game]
        collection.remove()
        document = {'Game': game}
        collection.insert(document)

    def get_game(self):
        collection = self.database[self.game]
        document = collection.find_one()
        game = document['Game']
        return game

    def add_game_update(self, game_update, session_number):
        game_update_item = self.get_game_update(session_number)
        if game_update_item is None:
            pass
        else:
            self.remove_game_update(session_number)
        collection = self.database[self.gameUpdates]
        document = {'GameUpdate': game_update, 'SessionNumber': session_number}
        collection.insert(document)

    def get_game_updates(self):
        collection = self.database[self.gameUpdates]
        documents = collection.find()
        if documents is None:
            return None
        game_updates = []
        for document in documents:
            game_updates.append(document['GameUpdate'])
        return game_updates

    def get_game_update(self, session_number):
        collection = self.database[self.gameUpdates]
        document = collection.find_one({"SessionNumber": session_number})
        if document is None:
            return None
        game_update = document['GameUpdate']
        return game_update

    def remove_game_update(self, session_number):
        collection = self.database[self.gameUpdates]
        document = collection.find_one({"SessionNumber": session_number})
        if document is None:
            return False
        else:
            collection.remove({'SessionNumber': session_number})
            return True

    def set_game_information(self, game_information):
        collection = self.database[self.game]
        collection.remove()
        document = {'GameInformation': game_information}
        collection.insert(document)

    def get_game_information(self):
        collection = self.database[self.game]
        document = collection.find_one()
        game_information = document['GameInformation']
        return game_information

    def add_chat_message(self, chat_message, game_session_number):
        chat_message_item = self.get_chat_message(game_session_number)
        if chat_message_item is None:
            pass
        else:
            self.remove_chat_message(game_session_number)
        collection = self.database[self.chatMessages]
        document = {'ChatMessage': chat_message, 'SessionNumber': game_session_number}
        collection.insert(document)

    def get_chat_message(self, game_session_number):
        collection = self.database[self.chatMessages]
        document = collection.find_one({"SessionNumber": game_session_number})
        if document is None:
            return None
        chat_message = document['ChatMessage']
        return chat_message

    def remove_chat_message(self, game_session_number):
        collection = self.database[self.chatMessages]
        document = collection.find_one({"SessionNumber": game_session_number})
        if document is None:
            return False
        else:
            collection.remove({'SessionNumber': game_session_number})
            return True


class GameEngine:
    def __init__(self, port):
        #global http_client
        #global server
        print "LocalHost: " + str(port)

        global http_client
        http_client = httplib.HTTPConnection(server['ip'], server['port'])
        http_body = json.dumps(server_game_engine_game_inform_request({'Title': 'Test'}))
        send_server_http_message(http_body)

        http_ioloop = tornado.ioloop.IOLoop.instance()
        application = tornado.web.Application([
            (r"/(.*)", HTTPBaseHandler)
        ])
        application.add_handlers(r"(.*)", [(r'/ws', WebSocketBaseHandler)], )
        http_server = tornado.httpserver.HTTPServer(application)
        http_server.listen(port)
        try:
            http_ioloop.start()
        except KeyboardInterrupt:
            pass


def send_server_http_message(http_body):
    global http_client
    http_client.request("POST", "/", http_body)
    response = http_client.getresponse()
    print response.read()
    http_client.close()


def process_message(data):
    request_type = data["Type"]
    response_source = data["Source"]
    if response_source == "Client":
        if request_type == 'Game Session Request':
            message = client_game_engine_game_session_request_handler(data)
        elif request_type == 'Game Chat':
            message = client_game_engine_chat_handler(data)
        elif request_type == 'Get Game Chat':
            message = client_game_engine_get_chat_handler(data)
        elif request_type == 'Get Game Update':
            message = client_game_engine_get_game_update_handler(data)
        elif request_type == 'Game Command':
            message = client_game_engine_game_command_request_handler(data)
        elif request_type == 'Terminate Game':
            message = client_game_engine_terminate_game_request_handler(data)
        elif request_type == 'Success':
            message = client_game_engine_success_request_handler(data)
        elif request_type == 'Fail':
            message = client_game_engine_fail_request_handler(data)
        elif request_type == 'Error':
            message = client_game_engine_error_request_handler(data)
        else:
            message = client_game_engine_error_request_handler(data)
        return message
    elif response_source == "Server":
        if request_type == 'Session Inform':
            message = server_game_engine_server_session_inform_handler(data)
        elif request_type == 'Success':
            message = server_game_engine_success_request_handler(data)
        elif request_type == 'Error':
            message = server_game_engine_error_request_handler(data)
        else:
            message = server_game_engine_error_request_handler(data)
        return message


class HTTPBaseHandler(tornado.web.RequestHandler):
    def get(self, call):
        global database
        try:
            data = json.loads(self.request.body)
            response = process_message(data)
            sessionNumber = response['SessionNumber']
            if database.get_http_client(sessionNumber) is None:
                database.add_http_client(sessionNumber)
            else:
                pass
            self.write(json.dumps(response))
            self.finish()
        except:
            # log error message
            pass

    def post(self, call):
        global database
        try:
            print "Command Received: \n" + str(self.request.body)
            data = json.loads(self.request.body)
            response = process_message(data)
            sessionNumber = response['SessionNumber']
            #if database.get_http_client(sessionNumber) is None:
            #    database.add_http_client(sessionNumber)
            #else:
            #    pass
            self.write(json.dumps(response))
            self.finish()
        except:
            # log error message
            pass


class WebSocketBaseHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        global webSocketClients
        webSocketClients.append(self)
        print "WebSocket Connected"

    def on_message(self, request):
        data = json.loads(request)
        response = process_message(data)
        self.write_message(json.dumps(response))

    def on_close(self):
        global webSocketClients
        if self in webSocketClients:
            webSocketClients.remove(self)


#Server - Client
#Requests
def client_game_engine_chat_request(data):
    response = data
    global source
    response["Source"] = source
    return response


#Responses
#Handle Game Session Request
def client_game_engine_game_session_request_handler(data):
    response = client_game_engine_session_response(data)
    return response


def client_game_engine_session_response(data):
    username = data["Username"]
    session_number = data["SessionNumber"]
    player_name = data["PlayerName"]
    if client_game_engine_authenticate_server_session(username, session_number, player_name):
        session_number = client_game_engine_create_game_session(data)
        if client_game_engine_game_session_valid(session_number, data["PlayerName"]):
            response = client_game_engine_success_response(data)
        else:
            response = client_game_engine_fail_response(data)
    else:
        response = client_game_engine_fail_response(data)
    global source
    response["Source"] = source
    return response


def client_game_engine_create_game_session(data):
    global database
    session_number = data['SessionNumber']
    player_name = data["PlayerName"]
    session = database.get_game_session(session_number)
    if session is None:
        session = {'SessionNumber': session_number, 'PlayerName': player_name}
    else:
        session['PlayerName'] = player_name
        database.remove_game_session(session_number)
    session_number = database.add_game_session(session)
    return database.get_game_session(session_number)


def client_game_engine_create_player(player_name):
    global database
    player = {"PlayerName": player_name}
    database.add_player(player)


#Handle Game Chat Request
def client_game_engine_chat_handler(data):
    global webSocketClients
    message = client_game_engine_chat_response(data)
    for webSocketClient in webSocketClients:
        webSocketClient.write_message(message)
    return message

    #httpClients = database.get_http_clients()
    #for httpClient in httpClients:
    #    session_number = httpClient['SessionNumber']
    #    database.add_message(response, session_number)


def client_game_engine_chat_response(data):
    session_number = data['SessionNumber']
    #if client_game_engine_game_session_valid(session_number, data["PlayerName"]):
    response = data
    #else:
    #    response = client_game_engine_fail_response(data)
    global source
    response["Source"] = source
    return response


#Handle Get Game Chat Request
def client_game_engine_get_chat_handler(data):
    return client_game_engine_get_chat_response(data)


def client_game_engine_get_chat_response(data):
    global database
    session_number = data["SessionNumber"]
    player_name = data["PlayerName"]
    if client_game_engine_game_session_valid(session_number, player_name):
        response = database.get_chat_message(session_number)
        if response is None:
            response = client_game_engine_error_response(data)
    else:
        response = client_game_engine_fail_response(data)
    global source
    response["Source"] = source
    return response


#Handle Get Game Update
def client_game_engine_get_game_update_handler(data):
    return client_game_engine_game_update_response(data)


def client_game_engine_game_update_response(data):
    if client_game_engine_game_session_valid(data["SessionNumber"], data["PlayerName"]):
        response = client_game_engine_get_game_update(data)
    else:
        response = client_game_engine_fail_response(data)
    global source
    response["Source"] = source
    return response


def client_game_engine_get_game_update(data):
    session_number = data["SessionNumber"]
    global database
    return database.get_game_update(session_number)


#Handle Game Command
def client_game_engine_game_command_request_handler(data):
    return client_game_engine_game_command_response(data)


def client_game_engine_game_command_response(data):
    if client_game_engine_game_session_valid(data["SessionNumber"], data["PlayerName"]):
        client_game_engine_execute_command(data)
        response = client_game_engine_get_game_update(data)
    else:
        response = client_game_engine_fail_response(data)
    global source
    response["Source"] = source
    return response


def client_game_engine_execute_command(data):
    #global database
    #return database.get_game()
    pass


#Handle Terminate Game
def client_game_engine_terminate_game_request_handler(data):
    return client_game_engine_terminate_game_response(data)


def client_game_engine_terminate_game_response(data):
    if client_game_engine_game_session_valid(data["SessionNumber"], data["PlayerName"]):
        if client_game_engine_terminate_session(data["SessionNumber"]):
            response = client_game_engine_success_response(data)
        else:
            response = client_game_engine_error_response(data)
    else:
        response = client_game_engine_fail_response(data)
    global source
    response["Source"] = source
    return response


def client_game_engine_terminate_session(session_number):
    global database
    session = database.get_game_session(session_number)
    if session is None:
        return False
    else:
        database.remove_game_session(session_number)
        return True


#Handle Success
def client_game_engine_success_request_handler(data):
    print data
    return {}


def client_game_engine_success_response(data):
    command = data["Type"]
    session_number = data["SessionNumber"]
    username = data["Username"]
    message = "Everything seems okay"
    response = {'Type': 'Success', 'SessionNumber': session_number, 'Username': username, 'Command': command,
                'Message': message}
    global source
    response["Source"] = source
    return response


#Handle Fail
def client_game_engine_fail_request_handler(data):
    print data
    return {}


def client_game_engine_fail_response(data):
    command = data["Type"]
    session_number = data["SessionNumber"]
    username = data["PlayerName"]
    message = "Action may only be performed by authenticated clients"
    response = {'Type': 'Fail', 'SessionNumber': session_number, 'Username': username, 'Command': command,
                'Message': message}
    global source
    response["Source"] = source
    return response


#Handle Error
def client_game_engine_error_request_handler(data):
    print data
    return client_game_engine_error_response(data)


def client_game_engine_error_response(data):
    command = data["Type"]
    session_number = data["SessionNumber"]
    username = data["Username"]
    message = "Something went wrong"
    response = {'Type': 'Error', 'SessionNumber': session_number, 'Username': username, 'Command': command,
                'Message': message}
    global source
    response["Source"] = source
    return response


def client_game_engine_game_session_valid(session_number, player_name):
    global database
    document = database.get_session(session_number)
    if document is None:
        return False
    else:
        if player_name == document["PlayerName"]:
            return True
        else:
            return False


#Validate
def client_game_engine_authenticate_server_session(username, server_session, player_name):
    if client_game_engine_server_session_valid(server_session, username):
        if client_game_engine_player_exists(player_name):
            client_game_engine_associate_player_and_session(player_name, server_session)
            return True
        else:
            client_game_engine_create_player(player_name)
            client_game_engine_associate_player_and_session(player_name, server_session)
            return True
    else:
        return False


def client_game_engine_server_session_valid(session_number, username):
    global database
    server_session = database.get_server_session(session_number)
    if server_session is None:
        return False
    elif username == server_session['Username']:
        return True
    else:
        return False


def client_game_engine_game_session_valid(session_number, player_name):
    global database
    game_session = database.get_server_session(session_number)
    if game_session is None:
        return False
    elif player_name == game_session['PlayerName']:
        return True
    else:
        return False


def client_game_engine_player_exists(player_name):
    global database
    if database.get_player(player_name) is None:
        return False
    else:
        return True


def client_game_engine_associate_player_and_session(player_name, server_session):
    global database
    player = database.get_player(player_name)
    player['Server Session'] = server_session
    database.remove_player(player_name)
    database.add_player(player)


#Server - Game Engine
#Requests
def server_game_engine_game_inform_request(game_info):
    global source
    request = {'Type': 'Game Inform', 'GameInfo': game_info, 'Ip': '127.0.0.1', 'Port': 6500, 'Source': source}
    return request


def server_game_engine_get_server_session_inform_request():
    global source
    request = {'Type': 'Get Game Inform', 'Source': source}
    return request


#Responses
#Handle Server Session Inform
def server_game_engine_server_session_inform_handler(data):
    return server_game_engine_server_session_inform_response(data)


def server_game_engine_server_session_inform_response(data):
    sessions = data['Sessions']
    for session in sessions:
        server_game_engine_add_session(session)


def server_game_engine_add_session(session):
    global database
    sessionNumber = session['SessionNumber']
    player_name = session['PlayerName']
    document = {'SessionNumber': sessionNumber, 'PlayerName': player_name}
    if database.get_session(sessionNumber) is None:
        database.add_session(document)
    else:
        database.remove_session(sessionNumber)
        database.add_session(document)


#Handle Success
def server_game_engine_success_request_handler(data):
    print data
    return {}


def server_game_engine_success_response(data):
    command = data["Type"]
    session_number = data["SessionNumber"]
    username = data["Username"]
    message = "Everything seems okay"
    response = {'Type': 'Success', 'SessionNumber': session_number, 'Username': username, 'Command': command,
                'Message': message}
    global source
    response["Source"] = source
    return response


#Handle Error
def server_game_engine_error_request_handler(data):
    print data
    return server_game_engine_error_response(data)


def server_game_engine_error_response(data):
    command = data["Type"]
    session_number = data["SessionNumber"]
    username = data["Username"]
    message = "Something went wrong"
    response = {'Type': 'Error', 'SessionNumber': session_number, 'Username': username, 'Command': command,
                'Message': message}
    global source
    response["Source"] = source
    return response


if __name__ == "__main__":
    try:
        import sys

        main(sys.argv[1])
    except:
        main()
    else:
        pass