import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
import json

webSocketClients = []

def main(port=6500):
    print "LocalHost: " + str(port)
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


class HTTPBaseHandler(tornado.web.RequestHandler):
    def get(self, call):
        print "Command Received: \n" + str(self.request.body)
        try:
            self.finish()
        except:
            # log error message
            pass

    def post(self, call):
        try:
            print "Command Received: \n" + str(self.request.body)
            data = json.loads(self.request.body)
            response = request_handler(data)
            self.write(json.dumps(response))
            self.finish()
        except:
            # log error message
            pass


class WebSocketBaseHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print "WebSocket Opened"
        webSocketClients.append(self)

    def on_command(self, request):
        data = json.loads(request)
        response = request_handler(data)
        self.write_command(response)

    def on_close(self):
        print "WebSocket Opened"
        webSocketClients.remove(self)


def request_handler(data):
    request_type = data["Type"]
    if request_type == 'Game Chat':
        message = chat_handler(data)
    elif request_type == 'Server Session Inform':
        response = server_session_inform_handler(data)
    elif request_type == 'Game Session Request':
        response = game_session_request_handler(data)
    elif request_type == 'Game Update Request':
        response = game_update_request_handler(data)
    elif request_type == 'Game Command':
        response = game_command_request_handler(data)
    elif request_type == 'Success':
        response = sucesss_request_handler(data)
    elif request_type == 'Fail':
        response = fail_request_handler(data)
    elif request_type == 'Terminate Game':
        response = terminate_game_request_handler(data)
    elif request_type == 'Error':
        response = error_request_handler(data)
    else:
        response = error_request_handler(data)
    return response


def chat_handler(data):
    for webSocketClient in webSocketClients:
        webSocketClient.write_message(data)
    return chat_response(data)


def chat_response(data):
    return data


def server_session_inform_handler(data):
    return server_session_inform_response(data)


def server_session_inform_response(data):
    add_session(data)
    return data


def add_session(data):
    pass


def game_session_request_handler(data):
    response = session_response(data)
    return response


def create_game_session(data):
    return data["Session"]


def session_response(data):
    if authenticate_server_session(data["Username"], data["Session"], data["Player Name"]):
        session = create_game_session(data)
        if game_session_valid(session, data["Player Name"]):
            command = "Session Request"
            message = "Authentication successful"
            response = {'Type': 'Success', 'Session': session, 'Command': command, 'Message': message}
            return response
        else:
            command = "Authentication Failure"
            message = "Authentication unsuccessful - invalid username or password"
            response = {'Type': 'Fail', 'Session': session, 'Command': command, 'Message': message}
            return response
    else:
        command = "Authentication Failure"
        message = "Authentication unsuccessful - invalid username or password"
        response = {'Type': 'Fail', 'Session': data["Session"], 'Player Name': data["Player Name"], 'Command': command, 'Message': message}
        return response


def authenticate_server_session(username, session, player):
    if server_session_valid(session, username):
        if player_exists(player):
            associate_player_and_session(player, session)
            return True
        else:
            create_player(player)
            associate_player_and_session(player, session)
            return True
    else:
        command = "Authentication Failure"
        message = "Authentication unsuccessful - invalid username or player"
        response = {'Type': 'Fail', 'Session': session, 'Player Name': player, 'Command': command, 'Message': message}
        return False


def server_session_valid(session, username):
    return True


def player_exists(player):
    return True


def associate_player_and_session(player, session):
    pass


def create_player(player):
    pass


def game_update_request_handler(data):
    return game_update_response(data)


def game_update_response(data):
    if game_session_valid(data["Session"], data["Player Name"]):
        response = get_game_update(data)
    else:
        command = "Authentication Failure"
        message = "Action may only be performed by authenticated clients"
        response = {'Type': 'Fail', 'Session': ["Session"], 'Player Name': data["Player Name"], 'Command': command, 'Message': message}
    return response


def get_game_update(data):
    return {}


def game_command_request_handler(data):
    return game_command_response(data)


#def update_game(data):
#    return {}


def game_command_response(data):
    if game_session_valid(data["Session"], data["Player Name"]):
        execute_command(data)
        response = get_game_update(data)
        return response
    else:
        command = "Authentication Failure"
        message = "Action may only be performed by authenticated clients"
        response = {'Type': 'Fail', 'Session': ["Session"], 'Player Name': data["Player Name"], 'Command': command, 'Message': message}
        return response


def execute_command(data):
    pass


def sucesss_request_handler(data):
    return success_response(data)


def success_response(data):
    if game_session_valid(data["Session"], data["Player Name"]):
        print "Session: " + str(data["Session"])
        print "Player: " + str(data["Player Name"])
        print "Request:" + str(data["Command"])
        print "Success: " + str(data["Message"])
        response = {}
    else:
        command = "Authentication Failure"
        message = "Action may only be performed by authenticated clients"
        response = {'Type': 'Fail', 'Session': data["Session"], 'Player Name': data["Player Name"], 'Command': command, 'Message': message}
    return response


def fail_request_handler(data):
    return fail_response(fail_response(data))


def fail_response(data):
    if game_session_valid(data["Session"], data["Player Name"]):
        print "Session: " + str(data["Session"])
        print "Player: " + str(data["Player Name"])
        print "Request:" + str(data["Command"])
        print "Fail: " + str(data["Message"])
        response = {}
    else:
        command = "Authentication Failure"
        message = "Action may only be performed by authenticated clients"
        response = {'Type': 'Fail', 'Session': data["Session"], 'Player Name': data["Player Name"], 'Command': command, 'Message': message}
    return response


def terminate_game_request_handler(data):
    return terminate_game_response(data)


def terminate_game_response(data):
    if game_session_valid(data["Session"], data["Player Name"]):
        if terminate_session(data["Session"]):
            command = "Game Terminate"
            message = "Termination successful"
            response = {'Type': 'Success', 'Session': data["Session"], 'Player Name': data["Player Name"], 'Command': command, 'Message': message}
        else:
            response = error_response(data["Session"])
    else:
        command = "Authentication Failure"
        message = "Action may only be performed by authenticated clients"
        response = {'Type': 'Fail', 'Session': data["Session"], 'Player Name': data["Player Name"], 'Command': command, 'Message': message}
    return response


def terminate_session(session):
    return True


def error_request_handler(data):
    return error_response(data)


def error_response(data):
    print data
    return data


def game_session_valid(session, player):
    return True


if __name__ == "__main__":
    try:
        import sys

        main(sys.argv[1])
    except:
        main()
    else:
        pass