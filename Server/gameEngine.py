import tornado.httpserver
import tornado.ioloop
import tornado.web
import json


def main(port=6500):
    print "LocalHost: " + str(port)
    ioloop = tornado.ioloop.IOLoop.instance()
    application = tornado.web.Application([
        (r"/(.*)", BaseHandler)
    ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(port)
    try:
        ioloop.start()
    except KeyboardInterrupt:
        pass


class BaseHandler(tornado.web.RequestHandler):
    def get(self, call):
        print "Message Received: \n" + str(self.request.body)
        try:
            self.finish()
        except:
            # log error message
            pass

    def post(self, call):
        try:
            print "Message Received: \n" + str(self.request.body)
            data = json.loads(self.request.body)
            #self.write(data["Type"]
            requestType = data["Type"]
            if requestType == 'Server Session Inform':
                message = server_session_inform_handler(data)
            elif requestType == 'Game Session Request':
                message = game_session_request_handler(data)
            elif requestType == 'Game Update Request':
                message = game_update_request_handler(data)
            elif requestType == 'Game Command':
                message = game_command_request_handler(data)
            elif requestType == 'Success':
                message = sucesss_request_handler(data)
            elif requestType == 'Fail':
                message = fail_request_handler(data)
            elif requestType == 'Terminate Game':
                message = terminate_game_request_handler(data)
            elif requestType == 'Error':
                message = error_request_handler(data)
            else:
                message = error_request_handler(data)

            self.write(json.dumps(message))

            self.finish()
        except:
            # log error message
            pass


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
            message = "Session Request"
            detail = "Authentication successful"
            response = {'Type': 'Success', 'Session': session, 'Message': message, 'Detail': detail}
            return response
        else:
            message = "Authentication Failure"
            detail = "Authentication unsuccessful - invalid username or password"
            response = {'Type': 'Fail', 'Session': session, 'Message': message, 'Detail': detail}
            return response
    else:
        message = "Authentication Failure"
        detail = "Authentication unsuccessful - invalid username or password"
        response = {'Type': 'Fail', 'Session': data["Session"], 'Player Name': data["Player Name"], 'Message': message, 'Detail': detail}
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
        message = "Authentication Failure"
        detail = "Authentication unsuccessful - invalid username or player"
        response = {'Type': 'Fail', 'Session': session, 'Player Name': player, 'Message': message, 'Detail': detail}
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
        message = "Authentication Failure"
        detail = "Action may only be performed by authenticated clients"
        response = {'Type': 'Fail', 'Session': ["Session"], 'Player Name': data["Player Name"], 'Message': message, 'Detail': detail}
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
        message = "Authentication Failure"
        detail = "Action may only be performed by authenticated clients"
        response = {'Type': 'Fail', 'Session': ["Session"], 'Player Name': data["Player Name"], 'Message': message, 'Detail': detail}
        return response


def execute_command(data):
    pass


def sucesss_request_handler(data):
    return success_response(data)


def success_response(data):
    if game_session_valid(data["Session"], data["Player Name"]):
        print "Session: " + str(data["Session"])
        print "Player: " + str(data["Player Name"])
        print "Request:" + str(data["Message"])
        print "Success: " + str(data["Detail"])
        response = ""
    else:
        message = "Authentication Failure"
        detail = "Action may only be performed by authenticated clients"
        response = {'Type': 'Fail', 'Session': data["Session"], 'Player Name': data["Player Name"], 'Message': message, 'Detail': detail}
    return response


def fail_request_handler(data):
    return fail_response(fail_response(data))


def fail_response(data):
    if game_session_valid(data["Session"], data["Player Name"]):
        print "Session: " + str(data["Session"])
        print "Player: " + str(data["Player Name"])
        print "Request:" + str(data["Message"])
        print "Fail: " + str(data["Detail"])
        response = ""
    else:
        message = "Authentication Failure"
        detail = "Action may only be performed by authenticated clients"
        response = {'Type': 'Fail', 'Session': data["Session"], 'Player Name': data["Player Name"], 'Message': message, 'Detail': detail}
    return response


def terminate_game_request_handler(data):
    return terminate_game_response(data)


def terminate_game_response(data):
    if game_session_valid(data["Session"], data["Player Name"]):
        if terminate_session(data["Session"]):
            message = "Game Terminate"
            detail = "Termination successful"
            response = {'Type': 'Success', 'Session': data["Session"], 'Player Name': data["Player Name"], 'Message': message, 'Detail': detail}
        else:
            response = error_response(data["Session"])
    else:
        message = "Authentication Failure"
        detail = "Action may only be performed by authenticated clients"
        response = {'Type': 'Fail', 'Session': data["Session"], 'Player Name': data["Player Name"], 'Message': message, 'Detail': detail}
    return response


def terminate_session(session):
    return True


def error_request_handler(data):
    print data
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