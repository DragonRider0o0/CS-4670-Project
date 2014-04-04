
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.httpclient import AsyncHTTPClient
import json


gameEngine = None
database = None
webSocketClients = {}
mongoClient = None
webSocketIndex = 0
serverClient = None
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
        web_sockets = "WebSockets"
        http_clients = "HTTPClients"
        users = "Users"
        game = "Game"
        server_sessions = "ServerSessions"
        sessions = "Sessions"
        players = "Players"
        messages = "Messages"
        database = None
        sessionNumber_count = 0

        def __init__(self):
            global mongoClient
            from pymongo import MongoClient
            mongoClient = MongoClient()
            self.database = mongoClient[self.name]

        def get_web_sockets(self):
            collection = self.database[self.web_sockets]
            documents = collection.find()
            dbIndexes = []
            for document in documents:
                dbIndexes.append(document['WebSocket'])
            return dbIndexes

        def get_http_clients(self):
            collection = self.database[self.http_clients]
            documents = collection.find()
            dbIndexes = []
            for document in documents:
                dbIndexes.append(document['HTTPClient'])
            return dbIndexes

        def get_http_client(self, sessionNumber_number):
            collection = self.database[self.http_clients]
            document = collection.find_one({"SessionNumber": sessionNumber_number})
            return document

        def get_server_session(self, sessionNumber_number):
            collection = self.database[self.server_sessions]
            document = collection.find_one({"SessionNumber": sessionNumber_number})
            return document

        def get_game(self):
            collection = self.database[self.game]
            document = collection.find_one()
            return document

        def get_user(self, username):
            collection = self.database[self.users]
            document = collection.find_one({"Username": username})
            return document

        def get_player(self, player_name):
            collection = self.database[self.players]
            document = collection.find_one({"PlayerName": player_name})
            return document

        def get_session(self, sessionNumber_number):
            collection = self.database[self.sessionNumbers]
            document = collection.find_one({"SessionNumber": sessionNumber_number})
            return document

        def get_message(self, sessionNumber_number):
            collection = self.database[self.messages]
            document = collection.find_one({"SessionNumber": sessionNumber_number})
            message = document["Message"]
            return message

        def add_web_socket(self, web_socket):
            document = {"WebSocket": web_socket}
            collection = self.database[self.web_sockets]
            collection.insert(document)

        def add_htttp_client(self, sessionNumber):
            document = {"SessionNumber": sessionNumber}
            collection = self.database[self.http_clients]
            collection.insert(document)

        def set_game(self, game):
            collection = self.database[self.game]
            collection.remove()
            collection.insert(game)

        def add_user(self, user):
            collection = self.database[self.users]
            collection.insert(user)

        def add_player(self, player):
            collection = self.database[self.players]
            collection.insert(player)

        def add_message(self, message, sessionNumber):
            document = {'Message': message, 'SessionNumber': sessionNumber}
            collection = self.database[self.messages]
            collection.insert(document)

        def add_session(self, sessionNumber):
            collection = self.database[self.sessionNumbers]
            collection.insert(sessionNumber)

        def add_server_session(self, sessionNumber, username):
            document = {'SessionNumber': sessionNumber, 'Username': username}
            collection = self.database[self.server_sessions]
            collection.insert(document)

        def remove_web_socket(self, web_socket):
            collection = self.database[self.web_sockets]
            collection.remove({'WebSocket': web_socket})

        def remove_http_client(self, http_client):
            collection = self.database[self.http_clients]
            collection.remove({'HTTPClient': http_client})

        def remove_player(self, player_name):
            collection = self.database[self.players]
            collection.remove({'PlayerName': player_name})

        def remove_session(self, sessionNumber_number):
            collection = self.database[self.sessionNumbers]
            document = collection.find_one({"SessionNumber": sessionNumber_number})
            if document is None:
                return False
            else:
                collection.remove({'SessionNumber': sessionNumber_number})
                return True


class GameEngine:
    def __init__(self, port):
        print "LocalHost: " + str(port)
        global serverClient
        serverClient = AsyncHTTPClient()
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
    request = {'Type': 'Game Inform', 'GameInfo': game_info, 'Source': source}
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