import tornado.websocket
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.netutil
import json
import functools
import socket

client = None
webSocketClients = []

def main(port=5500):
    global client
    client = Server(port)




class Server:
    def __init__(self, port):
        print "LocalHost: " + str(port)
        http_ioloop = tornado.ioloop.IOLoop.instance()
        application = tornado.web.Application([
            (r"/(.*)", HTTPBaseHandler)
        ])
        application.add_handlers(r"(.*)", [(r'/ws', WebSocketBaseHandler)], )
        http_server = tornado.httpserver.HTTPServer(application)
        http_server.listen(port)

        #unix_socket = tornado.netutil.bind_unix_socket('/tmp/sock.sock')
        #tornado.netutil.add_accept_handler(unix_socket, tcp_base_handler())
        try:
            http_ioloop.start()
        #    tcp_ioloop.start()
        except KeyboardInterrupt:
            pass


    def setup(port):
        print "LocalHost: " + str(port)
        http_ioloop = tornado.ioloop.IOLoop.instance()
        application = tornado.web.Application([
            (r"/(.*)", HTTPBaseHandler)
        ])
        application.add_handlers(r"(.*)", [(r'/ws', WebSocketBaseHandler)], )
        http_server = tornado.httpserver.HTTPServer(application)
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
        if request_type == 'Server Chat':
            message = client_server_chat_handler(data)
        elif request_type == 'Server Session Request':
            message = client_server_session_request_handler(data)
        elif request_type == 'Game List Request':
            message = client_server_game_list_request_handler(data)
        elif request_type == 'Success':
            message = client_server_sucesss_request_handler(data)
        elif request_type == 'Fail':
            message = client_server_fail_request_handler(data)
        elif request_type == 'Terminate Session':
            message = client_server_terminate_session_request_handler(data)
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
        elif request_type == 'Fail':
            message = game_engine_server_fail_request_handler(data)
        elif request_type == 'Error':
            message = game_engine_server_error_request_handler(data)
        else:
            message = game_engine_server_error_request_handler(data)
        return message


class HTTPBaseHandler(tornado.web.RequestHandler):
        def get(self, call):
            #print "Message Received: \n" + str(self.request.body)
            try:
                data = json.loads(self.request.body)
                response = process_message(data)
                self.write(json.dumps(response))
                self.finish()
            except:
                # log error message
                pass

        def post(self, call):
            try:
                print "Message Received: \n" + str(self.request.body)
                data = json.loads(self.request.body)
                response = process_message(data)
                self.write(json.dumps(response))
                self.finish()
            except:
                # log error message
                pass


class WebSocketBaseHandler(tornado.websocket.WebSocketHandler):
        def open(self):
            global webSocketClients
            print "WebSocket Opened"
            webSocketClients.append(self)

        def on_message(self, request):
            data = json.loads(request)
            response = process_message(data)
            self.write_message(response)

        def on_close(self):
            global webSocketClients
            print "WebSocket Opened"
            webSocketClients.remove(self)


def client_server_chat_handler(data):
    global webSocketClients
    message = client_server_chat_response(data)
    for webSocketClient in webSocketClients:
        webSocketClient.write_message(message)
    return client_server_chat_response(message)


def client_server_chat_response(data):
    return data


def client_server_session_request_handler(data):
    client_server_authenticate_user(data["Username"], data["Password"])
    session = client_server_create_session(data)
    response = client_server_session_response(session)
    return response


def client_server_create_session(data):
    return data["Session"]


def client_server_session_response(session):
    if client_server_session_valid(session):
        command = "Session Request"
        message = "Authentication successful"
        response = {'Type': 'Success', 'Session': session, 'Command': command, 'Message': message}
        return response
    else:
        command = "Session Request"
        message = "Authentication unsuccessful - invalid username or password"
        response = {'Type': 'Fail', 'Session': session, 'Command': command, 'Message': message}
        return response

def client_server_authenticate_user(username, password):
    return True


def client_server_game_list_request_handler(data):
    return client_server_game_list_response(data["Features"], data["Session"])


def client_server_game_list_response(types, session):
    if client_server_session_valid(session):
        response = client_server_get_game_list(types)
    else:
        command = "Game List Response"
        message = "Action may only be performed by authenticated clients"
        response = {'Type': 'Fail', 'Session': session, 'Command': command, 'Message': message}
    return response


def client_server_sucesss_request_handler(data):
    return client_server_success_response(data)


def client_server_success_response(data):
    if client_server_session_valid(data["Session"]):
        #print "Session: " + str(data["Session"])
        #print "Player: " + str(data["Player Name"])
        #print "Request:" + str(data["Command"])
        #print "Success: " + str(data["Message"])
        response = {}
    else:
        command = "Success"
        message = "Action may only be performed by authenticated clients"
        response = {'Type': 'Fail', 'Session': data["Session"], 'Command': command, 'Message': message}
    return response


def client_server_fail_request_handler(data):
    return client_server_fail_response(data)


def client_server_fail_response(data):
    if client_server_session_valid(data["Session"]):
        #print "Session: " + str(data["Session"])
        #print "Player: " + str(data["Player Name"])
        #print "Request:" + str(data["Command"])
        #print "Fail: " + str(data["Message"])
        response = {}
    else:
        command = "Fail"
        message = "Action may only be performed by authenticated clients"
        response = {'Type': 'Fail', 'Session': data["Session"], 'Command': command, 'Message': message}
    return response


def client_server_terminate_session_request_handler(data):
    return client_server_terminate_response(data["Session"])


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
    return response


def client_server_sucesss_request_handler(data):
    return client_server_success_response(data)


def client_server_success_response(data):
    if client_server_session_valid(data["Session"]):
        #print "Session: " + str(data["Session"])
        #print "Player: " + str(data["Player Name"])
        #print "Request:" + str(data["Command"])
        #print "Success: " + str(data["Message"])
        response = {}
    else:
        command = "Success"
        message = "Action may only be performed by authenticated clients"
        response = {'Type': 'Fail', 'Session': data["Session"], 'Command': command, 'Message': message}
    return response


def client_server_fail_request_handler(data):
    return client_server_fail_response(data)


def client_server_fail_response(data):
    if client_server_session_valid(data["Session"]):
        #print "Session: " + str(data["Session"])
        #print "Player: " + str(data["Player Name"])
        #print "Request:" + str(data["Command"])
        #print "Fail: " + str(data["Message"])
        response = {}
    else:
        command = "Fail"
        message = "Action may only be performed by authenticated clients"
        response = {'Type': 'Fail', 'Session': data["Session"], 'Command': command, 'Message': message}
    return response


def client_server_terminate_session_request_handler(data):
    return client_server_terminate_response(data["Session"])

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
    return response


def client_server_terminate_session(session):
    return True


def client_server_error_request_handler(data):
    #print data
    return client_server_error_response(data)


def client_server_error_response(data):
    print data
    return data


def client_server_terminate_session(session):
    return True

def client_server_error_request_handler(data):
    #print data
    return client_server_error_response(data)

def client_server_error_response(data):
    print data
    return data


def client_server_session_valid(session):
    return True


def client_server_get_game_list(types):
    return {}


def game_engine_server_game_inform_request_handler(data):
    return game_engine_server_game_inform_response(data, data["Session"])


def game_engine_server_game_inform_response(data, session):
    if game_engine_server_session_valid(session):
        game_engine_server_add_game(data)
        command = "Game Inform"
        message = "Termination successful"
        response = {'Type': 'Success', 'Session': session, 'Command': command, 'Message': message}
        return response
    else:
        command = "Game Inform"
        message = "Action may only be performed by authenticated clients"
        response = {'Type': 'Fail', 'Session': session, 'Command': command, 'Message': message}
        return response


def game_engine_server_add_game(data):
    pass


def game_engine_server_sucesss_request_handler(data):
    return game_engine_server_success_response(data)


def game_engine_server_success_response(data):
    if (game_engine_server_session_valid(data["Session"])):
        #print "Session: " + str(data["Session"])
        #print "Player: " + str(data["Player Name"])
        #print "Request:" + str(data["Command"])
        #print "Success: " + str(data["Message"])
        response = {}
    else:
        command = "Success"
        message = "Action may only be performed by authenticated clients"
        response = {'Type': 'Fail', 'Session': data["Session"], 'Command': command, 'Message': message}
    return response


def game_engine_server_fail_request_handler(data):
    return game_engine_server_fail_response(data)


def game_engine_server_fail_response(data):
    if game_engine_server_session_valid(data["Session"]):
        #print "Session: " + str(data["Session"])
        #print "Player: " + str(data["Player Name"])
        #print "Request:" + str(data["Command"])
        #print "Fail: " + str(data["Message"])
        response = {}
    else:
        command = "Fail"
        message = "Action may only be performed by authenticated clients"
        response = {'Type': 'Fail', 'Session': data["Session"], 'Command': command, 'Message': message}
    return response


def game_engine_server_terminate_session_request_handler(data):
    return game_engine_server_terminate_response(data["Session"])


def game_engine_server_terminate_response(session):
    if game_engine_server_session_valid(session):
        if game_engine_server_terminate_session(session):
            command = "Session Terminate"
            message = "Termination successful"
            response = {'Type': 'Success', 'Session': session, 'Command': command, 'Message': message}
        else:
            response = game_engine_server_error_response(session)
    else:
        command = "Session Terminate"
        message = "Action may only be performed by authenticated clients"
        response = {'Type': 'Fail', 'Session': session, 'Command': command, 'Message': message}
    return response


def game_engine_server_terminate_session(session):
    return True


def game_engine_server_error_request_handler(data):
    #print data
    return game_engine_server_error_response(data)


def game_engine_server_error_response(data):
    print data
    return data


def game_engine_server_terminate_session(session):
    return True


def game_engine_server_error_request_handler(data):
    #print data
    return game_engine_server_error_response(data)


def game_engine_server_error_response(data):
    print data
    return data


def game_engine_server_session_valid(session):
    return True


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