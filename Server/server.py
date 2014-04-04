from operator import eq
import tornado.websocket
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.netutil
import json
from tornado.httpclient import AsyncHTTPClient
import pymongo
import functools
import socket

gameEngine = None
database = None
webSocketClients = {}
mongoClient = None
webSocketIndex = 0
source = "Server"


def main(port=5500):
    global database
    database = Database()
    global gameEngine
    server = Server(port)


class Database:
    name = "Server"
    games = "Games"
    users = "Users"
    sessions = "Sessions"
    messages = "Messages"
    database = None

    def __init__(self):
        global mongoClient
        from pymongo import MongoClient

        mongoClient = MongoClient()
        self.database = mongoClient[self.name]

    def get_games(self):
        collection = self.database[self.games]
        documents = collection.find()
        games = []
        for document in documents:
            games.append(document['Game'])
        return games

    def get_game(self, game_title):
        collection = self.database[self.games]
        document = collection.find_one({"Title": game_title})
        return document

    def get_user(self, username):
        collection = self.database[self.users]
        document = collection.find_one({"Username": username})
        return document

    def get_session(self, session_number):
        collection = self.database[self.sessions]
        document = collection.find_one({"SessionNumber": session_number})
        return document

    def get_message(self, session_number):
        collection = self.database[self.messages]
        document = collection.find_one({"SessionNumber": session_number})
        return document

    def add_game(self, game_info):
        collection = self.database[self.games]
        collection.insert(game_info)

    def add_user(self, user):
        collection = self.database[self.users]
        collection.insert(user)

    def add_message(self, message):
        collection = self.database[self.messages]
        collection.insert(message)

    def add_session(self, session):
        collection = self.database[self.sessions]
        collection.insert(session)

    def remove_message(self, session_number):
        collection = self.database[self.messages]
        document = collection.find_one({"SessionNumber": session_number})
        if document is None:
            return False
        else:
            collection.remove({'Session': session_number})
            return True

    def remove_game(self, game_title):
        collection = self.database[self.games]
        document = collection.find_one({"Title": game_title})
        if document is None:
            return False
        else:
            collection.remove({"Title": game_title})
            return True

    def remove_session(self, session_number):
        collection = self.database[self.sessions]
        document = collection.find_one({"SessionNumber": session_number})
        if document is None:
            return False
        else:
            collection.remove({'Session': session_number})
            return True


class Server:
    def __init__(self, port):
        print "LocalHost: " + str(port)
        global gameEngineClient
        gameEngineClient = AsyncHTTPClient()
        http_ioloop = tornado.ioloop.IOLoop.instance()
        application = tornado.web.Application([
            (r"/(.*)", HTTPBaseHandler)
        ])
        application.add_handlers(r"(.*)", [(r'/ws', WebSocketBaseHandler)], )
        http_server = tornado.httpserver.HTTPServer(application, xheaders=True)
        http_server.listen(port)

        #unix_socket = tornado.netutil.bind_unix_socket('/tmp/sock.sock')
        #tornado.netutil.add_accept_handler(unix_socket, tcp_base_handler())
        try:
            http_ioloop.start()
        #    tcp_ioloop.start()
        except KeyboardInterrupt:
            pass


def process_message(data):
    request_type = data["Type"]
    response_source = data["Source"]
    if response_source == "Client":
        if request_type == 'Server Session Request':
            message = client_server_session_request_handler(data)
        elif request_type == 'Server Chat':
            message = client_server_chat_handler(data)
        elif request_type == 'Get Server Chat':
            message = client_server_get_chat_handler(data)
        elif request_type == 'Get Game List':
            message = client_server_game_list_request_handler(data)
        elif request_type == 'Terminate Session':
            message = client_server_terminate_session_request_handler(data)
        elif request_type == 'Success':
            message = client_server_success_request_handler(data)
        elif request_type == 'Fail':
            message = client_server_fail_request_handler(data)
        elif request_type == 'Error':
            message = client_server_error_request_handler(data)
        else:
            message = client_server_error_request_handler(data)
        return message
    elif response_source == "Game Engine":
        if request_type == 'Game Inform':
            message = game_engine_server_game_inform_request_handler(data)
        elif request_type == 'Success':
            message = game_engine_server_sucesss_request_handler(data)
        elif request_type == 'Error':
            message = game_engine_server_error_request_handler(data)
        else:
            message = game_engine_server_error_request_handler(data)
        return message


class HTTPBaseHandler(tornado.web.RequestHandler):
    def get(self, call):
        print "Message Received: \n" + str(self.request.body)
        try:
            data = json.loads(self.request.body)
            #print "Client IP: " + self.request.remote_ip
            response = process_message(data)
            self.write(json.dumps(response))
            self.finish()
        except:
            # log error message
            pass

    def post(self, call):
        try:
            data = json.loads(self.request.body)
            #print "Client IP: " + self.request.remote_ip
            response = process_message(data)
            self.write(json.dumps(response))
            self.finish()
        except :
            print "Unexpected error:", sys.exc_info()[0]


class WebSocketBaseHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        global webSocketClients
        global webSocketIndex
        webSocketClients[webSocketIndex] = self

    def on_message(self, request):
        data = json.loads(request)
        response = process_message(data)
        self.write_message(response)

    def on_close(self):
        global webSocketClients
        print "WebSocket Opened"

        for index, webSocket in webSocketClients.items():
            if webSocket == self:
                del webSocketClients[index]
                break


#Server - Client
#Requests
def client_server_chat_request(data):
    response = data
    global source
    response["Source"] = source
    return response


#Responses
#Handle Session Request
def client_server_session_request_handler(data):
    client_server_authenticate_user(data["Username"], data["Password"])
    session = client_server_create_session(data)
    response = client_server_session_response(session)
    return response


def client_server_create_session(data):
    return data["SessionNumber"]


def client_server_session_response(session):
    if client_server_session_valid(session):
        command = "Session Request"
        message = "Authentication successful"
        response = {'Type': 'Success', 'Session': session, 'Command': command, 'Message': message}
    else:
        command = "Session Request"
        message = "Authentication unsuccessful - invalid username or password"
        response = {'Type': 'Fail', 'Session': session, 'Command': command, 'Message': message}
    global source
    response["Source"] = source
    return response


#Handle Server Chat
def client_server_chat_handler(data):
    global webSocketClients
    message = client_server_chat_response(data)
    global database
    for dbIndex in database.get_web_sockets():
        if dbIndex in webSocketClients:
            webSocketClients[dbIndex].write_message(message)

    return client_server_chat_response(message)


def client_server_chat_response(data):
    response = data
    global source
    response["Source"] = source
    return response


#Handle Get Server Chat
def client_server_get_chat_handler(data):
    return client_server_get_chat_response(data)


def client_server_get_chat_response(data):
    session_number = data["SessionNumber"]
    player_name = data["PlayerName"]
    if client_server_session_valid(session_number, player_name):
        response = database.get_message(session_number)
    else:
        command = "Authentication Failure"
        message = "Authentication unsuccessful - invalid username or password"
        response = {'Type': 'Fail', 'Session': session_number, 'Command': command, 'Message': message}
    global source
    response["Source"] = source
    return response


#Handle Game List Request
def client_server_game_list_request_handler(data):
    return client_server_game_list_response(data["SessionNumber"])


def client_server_game_list_response(session):
    if client_server_session_valid(session):
        response = client_server_get_game_list()
    else:
        command = "Game List Response"
        message = "Action may only be performed by authenticated clients"
        response = {'Type': 'Fail', 'Session': session, 'Command': command, 'Message': message}
    global source
    response["Source"] = source
    return response


def client_server_get_game_list():
    global database
    games = database.get_games()
    return games


#Handle Terminate Session
def client_server_terminate_session_request_handler(data):
    return client_server_terminate_response(data["SessionNumber"])


def client_server_terminate_response(session):
    if client_server_session_valid(session):
        if client_server_terminate_session(session):
            command = "Session Terminate"
            message = "Termination successful"
            response = {'Type': 'Success', 'Session': session, 'Command': command, 'Message': message}
        else:
            response = client_server_error_response(session)
    else:
        command = "Session Terminate"
        message = "Action may only be performed by authenticated clients"
        response = {'Type': 'Fail', 'Session': session, 'Command': command, 'Message': message}
    global source
    response["Source"] = source
    return response


def client_server_terminate_session(session):
    return True


#Handle Success
def client_server_success_request_handler(data):
    return client_server_success_response(data)


def client_server_success_response(data):
    if client_server_session_valid(data["SessionNumber"]):
        #print "Session: " + str(data["SessionNumber"])
        #print "Player: " + str(data["PlayerName"])
        #print "Request:" + str(data["Command"])
        #print "Success: " + str(data["Message"])
        response = {}
    else:
        command = "Success"
        message = "Action may only be performed by authenticated clients"
        response = {'Type': 'Fail', 'Session': data["SessionNumber"], 'Command': command, 'Message': message}
    global source
    response["Source"] = source
    return response


#Handle Fail
def client_server_fail_request_handler(data):
    return client_server_fail_response(data)


def client_server_fail_response(data):
    if client_server_session_valid(data["SessionNumber"]):
        #print "Session: " + str(data["SessionNumber"])
        #print "Player: " + str(data["PlayerName"])
        #print "Request:" + str(data["Command"])
        #print "Fail: " + str(data["Message"])
        response = {}
    else:
        command = "Fail"
        message = "Action may only be performed by authenticated clients"
        response = {'Type': 'Fail', 'Session': data["SessionNumber"], 'Command': command, 'Message': message}
    global source
    response["Source"] = source
    return response


#Handle Error
def client_server_error_request_handler(data):
    #print data
    return client_server_error_response(data)


def client_server_error_response(data):
    print data
    response = data
    global source
    response["Source"] = source
    return response


#Validation
def client_server_authenticate_user(username, password):
    global database
    user = database.get_user(username)
    if user is None:
        user['Username'] = username
        user['Password'] = password
        database.add_user(user)
    if user['Password'] is password:
        return True
    else:
        return False


def client_server_session_valid(session):
    global database
    if database.get_session(session) is None:
        return False
    else:
        return True


#Server - Game Engine
#Requests
def server_game_engine_server_session_inform_request(sessions):
    global source
    request = {'Type': 'Session Inform', 'Sessions': sessions, 'Source': source}
    return request


def server_game_engine_get_game_inform_request():
    global source
    request = {'Type': 'Get Game Inform', 'Source': source}
    return request


#Responses
#Handle Game Inform
def game_engine_server_game_inform_request_handler(data):
    return game_engine_server_game_inform_response(data)


def game_engine_server_game_inform_response(data):
    game_engine_server_add_game(data)
    return {}


def game_engine_server_add_game(data):

    global database
    game_info = data['GameInfo']
    game_title = game_info['Title']
    document = game_info
    if database.get_game(game_title) is None:
        database.add_game(document)
    else:
        database.remove_game(game_title)
        database.add_game(document)


#Handle Success
def game_engine_server_sucesss_request_handler(data):
    return game_engine_server_success_response(data)


def game_engine_server_success_response(data):
    print data
    return {}


#Handle Error
def game_engine_server_error_request_handler(data):
    return game_engine_server_error_response(data)


def game_engine_server_error_response(data):
    print data
    return {}


#def tcp_base_handler(sock, fd, events):
#    pass


if __name__ == "__main__":
    try:
        import sys

        main(sys.argv[1])
    except:
        main()
    else:
        pass