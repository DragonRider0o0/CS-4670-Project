
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.httpclient import AsyncHTTPClient
import json
#import urllib2
import httplib


gameEngine = None
database = None
webSocketClients = {}
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
    serverSessions = "ServerSessions"
    gameSessions = "GameSessions"
    players = "Players"
    game = "Game"
    gameUpdates = "GameUpdates"
    gameInformation = "GameInformation"
    chatMessages = "ChatMessages"
    database = None
    gameSessionNumber = 0

    def __init__(self):
        global mongoClient
        from pymongo import MongoClient
        mongoClient = MongoClient()
        self.database = mongoClient[self.name]

    def add_server_session(self, server_session):
        collection = self.database[self.serverSessions]
        server_session_number = server_session['SessionNumber']
        server_session_item = self.get_server_session(server_session_number)
        if server_session_item is None:
            pass
        else:
            self.remove_server_session(server_session_number)
        document = {'Session': server_session, 'SessionNumber': server_session_number}
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
            pass
        else:
            self.remove_game_session(game_session_number)
        document = {'Session': game_session, 'SessionNumber': game_session_number}
        collection.insert(document)

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
        global http_client
        global server
        print "LocalHost: " + str(port)

        global http_client
        http_client = httplib.HTTPConnection(server['ip'], server['port'])
        http_body = json.dumps(server_game_engine_game_inform_request({'Title': 'Test'}))
        send_server_http_message(http_body)

        http_ioloop = tornado.ioloop.IOLoop.instance()
        application = tornado.web.Application([
            (r"/(.*)", HTTPBaseHandler)
        ])
        application.add_handlers(r"(.*)", [(r'/ws', WebSocketBaseHandler)],)
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
        if request_type == 'Server Session Inform':
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
            if database.get_http_client(sessionNumber) is None:
                database.add_http_client(sessionNumber)
            else:
                pass
            self.write(json.dumps(response))
            self.finish()
        except:
            # log error message
            pass


class WebSocketBaseHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        global webSocketClients
        print "WebSocket Opened"
        global webSocketIndex
        webSocketClients[webSocketIndex] = self
        print "Adding websocket to database\n"
        global database
        database.add_web_socket(webSocketIndex)
        webSocketIndex += 1

    def on_message(self, request):
        data = json.loads(request)
        response = process_message(data)
        self.write_message(response)

    def on_close(self):
        global webSocketClients
        print "WebSocket Opened"
        dbIndex = None
        for index, webSocket in webSocketClients.items():
            if webSocket == self:
                dbIndex = index
                del webSocketClients[index]
                print "Removing websocket from database\n"
                global database
                database.remove_web_socket(dbIndex)
                break


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
    if client_game_engine_authenticate_server_session(data["Username"], data["SessionNumber"], data["PlayerName"]):
        sessionNumber = client_game_engine_create_game_session(data)
        if client_game_engine_game_session_valid(sessionNumber, data["PlayerName"]):
            command = "Session Request"
            message = "Authentication successful"
            response = {'Type': 'Success', 'SessionNumber': sessionNumber, 'Command': command, 'Message': message}
        else:
            command = "Authentication Failure"
            message = "Authentication unsuccessful - invalid username or password"
            response = {'Type': 'Fail', 'SessionNumber': sessionNumber, 'Command': command, 'Message': message}
    else:
        command = "Authentication Failure"
        message = "Authentication unsuccessful - invalid username or password"
        response = {'Type': 'Fail', 'SessionNumber': data["SessionNumber"], 'PlayerName': data["PlayerName"], 'Command': command, 'Message': message}
    global source
    response["Source"] = source
    return response


def client_game_engine_create_game_session(data):
    global database
    global sessionNumber_count
    sessionNumber = data["SessionNumber"]
    if database.get_session is None:
        sessionNumber = sessionNumber_count
        sessionNumber_count += 1
        database.add_session(sessionNumber)
    return sessionNumber


def client_game_engine_associate_player_and_session(player_name, server_session):
    global database
    player = database.get_player(player_name)
    player['Server Session'] = server_session
    database.remove_player(player_name)
    database.add_player(player)


def client_game_engine_create_player(player_name):
    global database
    player = {"PlayerName": player_name}
    database.add_player(player)


#Handle Game Chat Request
def client_game_engine_chat_handler(data):
    global database
    response = client_game_engine_chat_response(data)
    for webSocketClient in webSocketClients:
        webSocketClient.write_message(response)
    httpClients = database.get_http_clients()
    for httpClient in httpClients:
        sessionNumber = httpClient['SessionNumber']
        database.add_message(response, sessionNumber)
    return response


def client_game_engine_chat_response(data):
    sessionNumber = data['SessionNumber']
    if client_game_engine_game_session_valid(sessionNumber, data["PlayerName"]):
        response = data
    else:
        command = "Authentication Failure"
        message = "Authentication unsuccessful - invalid username or password"
        response = {'Type': 'Fail', 'SessionNumber': sessionNumber, 'Command': command, 'Message': message}
    global source
    response["Source"] = source
    return response


#Handle Get Game Chat Request
def client_game_engine_get_chat_handler(data):
    return client_game_engine_get_chat_response(data)


def client_game_engine_get_chat_response(data):
    global database
    sessionNumber = data["SessionNumber"]
    if client_game_engine_game_session_valid(sessionNumber, data["PlayerName"]):
        response = database.get_message(sessionNumber)
    else:
        command = "Authentication Failure"
        message = "Authentication unsuccessful - invalid username or password"
        response = {'Type': 'Fail', 'SessionNumber': sessionNumber, 'Command': command, 'Message': message}
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
        command = "Authentication Failure"
        message = "Action may only be performed by authenticated clients"
        response = {'Type': 'Fail', 'SessionNumber': ["SessionNumber"], 'PlayerName': data["PlayerName"], 'Command': command, 'Message': message}
    global source
    response["Source"] = source
    return response


def client_game_engine_get_game_update(data):
    global database
    return database.get_game()


#Handle Game Command
def client_game_engine_game_command_request_handler(data):
    return client_game_engine_game_command_response(data)


def client_game_engine_game_command_response(data):
    if client_game_engine_game_session_valid(data["SessionNumber"], data["PlayerName"]):
        client_game_engine_execute_command(data)
        response = client_game_engine_get_game_update(data)
    else:
        command = "Authentication Failure"
        message = "Action may only be performed by authenticated clients"
        response = {'Type': 'Fail', 'SessionNumber': ["SessionNumber"], 'PlayerName': data["PlayerName"], 'Command': command, 'Message': message}
    global source
    response["Source"] = source
    return response


def client_game_engine_execute_command(data):
    global database
    return database.get_game()


#Handle Terminate Game
def client_game_engine_terminate_game_request_handler(data):
    return client_game_engine_terminate_game_response(data)


def client_game_engine_terminate_game_response(data):
    if client_game_engine_game_session_valid(data["SessionNumber"], data["PlayerName"]):
        if client_game_engine_terminate_session(data["SessionNumber"]):
            command = "Game Terminate"
            message = "Termination successful"
            response = {'Type': 'Success', 'SessionNumber': data["SessionNumber"], 'PlayerName': data["PlayerName"], 'Command': command, 'Message': message}
        else:
            response = client_game_engine_error_response(data["SessionNumber"])
    else:
        command = "Authentication Failure"
        message = "Action may only be performed by authenticated clients"
        response = {'Type': 'Fail', 'SessionNumber': data["SessionNumber"], 'PlayerName': data["PlayerName"], 'Command': command, 'Message': message}
    global source
    response["Source"] = source
    return response


def client_game_engine_terminate_session(sessionNumber):
    global database
    if database.remove_session(sessionNumber) is None:
        return False
    else:
        return True


#Handle Success
def client_game_engine_success_request_handler(data):
    return client_game_engine_success_response(data)


def client_game_engine_success_response(data):
    print data
    return {}


#Handle Fail
def client_game_engine_fail_request_handler(data):
    return client_game_engine_fail_response(data)


def client_game_engine_fail_response(data):
    print data
    return {}


#Handle Error
def client_game_engine_error_request_handler(data):
    return client_game_engine_error_response(data)


def client_game_engine_error_response(data):
    print data
    response = data;
    global source
    response["Source"] = source
    return response


def client_game_engine_game_session_valid(sessionNumber, player_name):
    global database
    document = database.get_session(sessionNumber)
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
        command = "Authentication Failure"
        message = "Authentication unsuccessful - invalid username or player"
        response = {'Type': 'Fail', 'SessionNumber': server_session, 'PlayerName': player_name, 'Command': command, 'Message': message}
        return False


def client_game_engine_server_session_valid(sessionNumber, username):
    global database
    server_session = database.get_server_session(sessionNumber)
    if username == server_session['Username']:
        return True
    else:
        return False


def client_game_engine_player_exists(player_name):
    global database
    if database.get_player(player_name) is None:
        return False
    else:
        return True


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
    return server_game_engine_success_response(data)


def server_game_engine_success_response(data):
    print data
    return {}


#Handle Error
def server_game_engine_error_request_handler(data):
    return server_game_engine_error_response(data)


def server_game_engine_error_response(data):
    print data
    return {}


if __name__ == "__main__":
    try:
        import sys

        main(sys.argv[1])
    except:
        main()
    else:
        pass