import httplib
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
webSocketClients = []
mongoClient = None
webSocketIndex = 0
source = "Server"
game_engine = {
    'ip': "127.0.0.1",
    'port': '6500'
}


def main(port=5500):
    global database
    database = Database()
    global gameEngine
    server = Server(port)


class Database:
    name = "Server"
    gameEngines = "GameEngines"
    httpClients = "HTTPClients"
    sessions = "Sessions"
    users = "Users"
    gameInformations = "GameInformations"
    chatMessages = "ChatMessages"
    database = None
    serverSessionNumber = 0

    def __init__(self):
        global mongoClient
        from pymongo import MongoClient

        mongoClient = MongoClient()
        self.database = mongoClient[self.name]

    def clear_database(self):
        collection = self.database[self.gameEngines]
        collection.remove()
        collection = self.database[self.httpClients]
        collection.remove()
        collection = self.database[self.sessions]
        collection.remove()
        collection = self.database[self.users]
        collection.remove()
        collection = self.database[self.gameInformations]
        collection.remove()
        collection = self.database[self.chatMessages]
        collection.remove()

    def add_game_engine(self, game_engine):
        game_engines = self.get_game_engines()
        for game_engine_item in game_engines:
            if game_engine_item['Ip'] == game_engine['Ip'] and game_engine_item['Port'] == game_engine['Port']:
                return
            else:
                pass
        collection = self.database[self.gameEngines]
        document = {'GameEngine': game_engine}
        collection.insert(document)

    def get_game_engines(self):
        collection = self.database[self.gameEngines]
        documents = collection.find()
        if documents is None:
            return None
        game_engines = []
        for document in documents:
            game_engines.append(document['GameEngine'])
        return game_engines

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

    def add_session(self, session):
        collection = self.database[self.sessions]
        session_number = session['SessionNumber']
        session_item = self.get_session(session_number)
        if session_item is None:
            self.serverSessionNumber = collection.count() + 1
            collection.count()
            session['SessionNumber'] = self.serverSessionNumber
            document = {'_id': self.serverSessionNumber, 'Session': session, 'SessionNumber': self.serverSessionNumber}
            collection.insert(document)
            return self.serverSessionNumber
        else:
            if session_item["Username"] == session["Username"]:
                return session_number
            else:
                self.serverSessionNumber = collection.count() + 1
                session['SessionNumber'] = self.serverSessionNumber
                document = {'_id': self.serverSessionNumber, 'Session': session, 'SessionNumber': self.serverSessionNumber}
                collection.insert(document)
                return self.serverSessionNumber

    def get_sessions(self):
        collection = self.database[self.sessions]
        documents = collection.find()
        if documents is None:
            return None
        sessions = []
        for document in documents:
            sessions.append(document['Session'])
        return sessions

    def get_session(self, session_number):
        collection = self.database[self.sessions]
        document = collection.find_one({"SessionNumber": session_number})
        if document is None:
            return None
        session = document['Session']
        return session

    def remove_session(self, session_number):
        collection = self.database[self.sessions]
        document = collection.find_one({"SessionNumber": session_number})
        if document is None:
            return False
        else:
            collection.remove({'Session': session_number})
            return True

    def add_user(self, user):
        collection = self.database[self.users]
        username = user['Username']
        user_item = self.get_user(username)
        if user_item is None:
            pass
        else:
            self.remove_user(username)
        document = {'_id': username, 'User': user, 'Username': username}
        collection.insert(document)

    def get_user(self, username):
        collection = self.database[self.users]
        document = collection.find_one({"Username": username})
        if document is None:
            return None
        user = document['User']
        return user

    def remove_user(self, username):
        collection = self.database[self.users]
        document = collection.find_one({"Username": username})
        if document is None:
            return False
        else:
            collection.remove({'Username': username})
            return True

    def add_game_information(self, game_information):
        game_title = game_information['Title']
        game_information_item = self.get_game_information(game_title)
        if game_information_item is None:
            pass
        else:
            self.remove_game_information(game_title)
        collection = self.database[self.gameInformations]
        document = {'_id': game_title, 'GameInformation': game_information, 'Title': game_title}
        collection.insert(document)

    def get_game_informations(self):
        collection = self.database[self.gameInformations]
        documents = collection.find()
        if documents is None:
            return None
        game_informations = []
        for document in documents:
            game_informations.append(document['GameInformation'])
        return game_informations

    def get_game_information(self, game_title):
        collection = self.database[self.gameInformations]
        document = collection.find_one({"Title": game_title})
        if document is None:
            return None
        game_information = document['GameInformation']
        return game_information

    def remove_game_information(self, game_title):
        collection = self.database[self.gameInformations]
        document = collection.find_one({"Title": game_title})
        if document is None:
            return False
        else:
            collection.remove({'Title': game_title})
            return True

    def add_chat_message(self, chat_message, session_number):
        chat_message_item = self.get_chat_message(session_number)
        if chat_message_item is None:
            pass
        else:
            self.remove_chat_message(session_number)
        collection = self.database[self.chatMessages]
        document = {'ChatMessage': chat_message, 'SessionNumber': session_number}
        collection.insert(document)

    def get_chat_message(self, session_number):
        collection = self.database[self.chatMessages]
        document = collection.find_one({"SessionNumber": session_number})
        if document is None:
            return None
        chat_message = document['ChatMessage']
        return chat_message

    def remove_chat_message(self, session_number):
        collection = self.database[self.chatMessages]
        document = collection.find_one({"SessionNumber": session_number})
        if document is None:
            return False
        else:
            collection.remove({'SessionNumber': session_number})
            return True


class Server:
    def __init__(self, port):
        print "LocalHost: " + str(port)

        global http_client
        http_client = httplib.HTTPConnection(game_engine['ip'], game_engine['port'])
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


def send_game_engine_http_message(http_body):
    global http_client
    http_client.request("POST", "/", http_body)
    response = http_client.getresponse()
    print response.read()
    http_client.close()


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
            message = game_engine_server_success_request_handler(data)
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
def client_server_chat_request(data):
    response = data
    global source
    response["Source"] = source
    return response


#Responses
#Handle Session Request
def client_server_session_request_handler(data):
    global database
    username = data["Username"]
    password = data["Password"]
    client_server_authenticate_user(username, password)
    session = client_server_create_session(data)
    response = client_server_session_response(session)


    http_body = json.dumps(server_game_engine_server_session_inform_request());
    send_game_engine_http_message(http_body)

    return response


def client_server_create_session(data):
    global database
    session_number = data['SessionNumber']
    username = data['Username']
    session = database.get_session(session_number)
    if session is None:
        session = {'SessionNumber': session_number, 'Username': username}
    else:
        session['Username'] = username
        database.remove_session(session_number)
    session_number = database.add_session(session)
    return database.get_session(session_number)


def client_server_session_response(data):
    global database
    session_number = data["SessionNumber"]
    username = data["Username"]
    if client_server_session_valid(session_number, username):
        response = {'Type': 'Server Session', 'SessionNumber': session_number, 'Username': username}
    else:
        response = client_server_fail_response(data)
    global source
    response["Source"] = source
    return response


#Handle Server Chat
def client_server_chat_handler(data):
    global webSocketClients
    message = client_server_chat_response(data)
    for webSocketClient in webSocketClients:
        webSocketClient.write_message(message)
    return message


def client_server_chat_response(data):
    session_number = data['SessionNumber']
    username = data["Username"]
    if client_server_session_valid(session_number, username):
        response = data
    else:
        response = client_server_fail_response(data)
    global source
    response["Source"] = source
    return response


#Handle Get Server Chat
def client_server_get_chat_handler(data):
    return client_server_get_chat_response(data)


def client_server_get_chat_response(data):
    global database
    session_number = data["SessionNumber"]
    username = data["Username"]
    if client_server_session_valid(session_number, username):
        response = database.get_chat_message(session_number)
        if response is None:
            response = client_server_error_response(data)
    else:
        response = client_server_fail_response(data)
    response["Source"] = source
    return response


#Handle Game List Request
def client_server_game_list_request_handler(data):
    return client_server_game_list_response(data)


def client_server_game_list_response(data):
    session_number = data["SessionNumber"]
    username = data["Username"]
    if client_server_session_valid(session_number, username):
        game_list = client_server_get_game_list()
        response = {'Type': 'Game List', 'SessionNumber': session_number, 'Username': username, 'Games': game_list}
    else:
        response = client_server_fail_response(data)
    global source
    response["Source"] = source
    return response


def client_server_get_game_list():
    global database
    games = database.get_game_informations()
    return games


#Handle Terminate Session
def client_server_terminate_session_request_handler(data):
    return client_server_terminate_response(data)


def client_server_terminate_response(data):
    session_number = data["SessionNumber"]
    username = data["Username"]
    if client_server_session_valid(session_number, username):
        if client_server_terminate_session(session_number):
            response = client_server_success_response(data)
        else:
            response = client_server_error_response(data)
    else:
        response = client_server_fail_response(data)
    global source
    response["Source"] = source
    return response


def client_server_terminate_session(session_number):
    global database
    session = database.get_session(session_number)
    if session is None:
        return False
    else:
        database.remove_session(session_number)
        return True


#Handle Success
def client_server_success_request_handler(data):
    print data
    return {}


def client_server_success_response(data):
    command = data["Type"]
    session_number = data["SessionNumber"]
    username = data["Username"]
    message = "Everything seems okay"
    response = {'Type': 'Success', 'SessionNumber': session_number, 'Username': username, 'Command': command, 'Message': message}
    global source
    response["Source"] = source
    return response


#Handle Fail
def client_server_fail_request_handler(data):
    print data
    return client_server_fail_response(data)

def client_server_fail_response(data):
    command = data["Type"]
    session_number = data["SessionNumber"]
    username = data["Username"]
    message = "Action may only be performed by authenticated clients"
    response = {'Type': 'Fail', 'SessionNumber': session_number, 'Username': username, 'Command': command, 'Message': message}
    global source
    response["Source"] = source
    return response


#Handle Error
def client_server_error_request_handler(data):
    print data
    return client_server_error_response(data)


def client_server_error_response(data):
    command = data["Type"]
    session_number = data["SessionNumber"]
    username = data["Username"]
    message = "Something went wrong"
    response = {'Type': 'Error', 'SessionNumber': session_number, 'Username': username, 'Command': command, 'Message': message}
    global source
    response["Source"] = source
    return response


#Validation
def client_server_authenticate_user(username, password):
    global database
    user = database.get_user(username)
    if user is None:
        user = {'Username': username, 'Password': password}
        database.add_user(user)
    if user['Password'] is password:
        return True
    else:
        return False


def client_server_session_valid(session_number, username):
    global database
    session = database.get_session(session_number)
    if session is None:
        return False
    else:
        if session["Username"] == username:
            return True
        else:
            return False


#Server - Game Engine
#Requests
def server_game_engine_server_session_inform_request():
    global database
    global source

    sessions = database.get_sessions()
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

    #sessions = [{'SessionNumber': 0, 'Username': 'Test'}]
    #http_body = json.dumps(server_game_engine_server_session_inform_request(sessions))
    #send_game_engine_http_message(http_body)

    return {}


def game_engine_server_add_game(data):
    global database
    game_info = data['GameInfo']
    game_title = game_info['Title']
    document = game_info
    if database.get_game_information(game_title) is None:
        database.add_game_information(document)
    else:
        database.remove_game_information(game_title)
        database.add_game_information(document)


#Handle Success
def game_engine_server_success_request_handler(data):
    print data
    return {}


def game_engine_server_success_response(data):
    command = data["Type"]
    session_number = data["SessionNumber"]
    username = data["Username"]
    message = "Everything seems okay"
    response = {'Type': 'Success', 'SessionNumber': session_number, 'Username': username, 'Command': command, 'Message': message}
    global source
    response["Source"] = source
    return response


#Handle Error
def game_engine_server_error_request_handler(data):
    print data
    return game_engine_server_error_response(data)


def game_engine_server_error_response(data):
    command = data["Type"]
    session_number = data["SessionNumber"]
    username = data["Username"]
    message = "Something went wrong"
    response = {'Type': 'Error', 'SessionNumber': session_number, 'Username': username, 'Command': command, 'Message': message}
    global source
    response["Source"] = source
    return response


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