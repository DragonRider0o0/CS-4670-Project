import tornado.httpserver
import tornado.ioloop
import tornado.web
import json


def main(port=5500):
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
            #self.write(data["Type"])
            requestType = data["Type"]
            if requestType == 'Chat':
                message = chat_handler(data)
            elif requestType == 'Server Session Request':
                message = session_request_handler(data)
            elif requestType == 'Game List Request':
                message = game_list_request_handler(data)
            elif requestType == 'Game Inform':
                message = game_inform_request_handler(data)
            elif requestType == 'Success':
                message = sucesss_request_handler(data)
            elif requestType == 'Fail':
                message = fail_request_handler(data)
            elif requestType == 'Terminate Session':
                message = terminate_session_request_handler(data)
            elif requestType == 'Error':
                message = error_request_handler(data)
            else:
                message = error_request_handler(data)

            self.write(json.dumps(message))

            self.finish()
        except:
            # log error message
            pass


def chat_handler(data):
    return chat_response(data)


def chat_response(data):
    return data


def session_request_handler(data):
    authenticate_user(data["Username"], data["Password"])
    session = create_session(data)
    response = session_response(session)
    return response


def create_session(data):
    return data["Session"]


def session_response(session):
    if session_valid(session):
        message = "Session Request"
        detail = "Authentication successful"
        response = {'Type': 'Success', 'Session': session, 'Message': message, 'Detail': detail}
        return response
    else:
        message = "Authentication Failure"
        detail = "Authentication unsuccessful - invalid username or password"
        response = {'Type': 'Fail', 'Session': session, 'Message': message, 'Detail': detail}
        return response


def authenticate_user(username, password):
    return True


def game_list_request_handler(data):
    return game_list_response(data["Client Type"], data["Session"])


def game_list_response(types, session):
    if session_valid(session):
        response = get_game_list(types)
    else:
        message = "Not authenticated"
        detail = "Action may only be performed by authenticated clients"
        response = {'Type': 'Fail', 'Session': session, 'Message': message, 'Detail': detail}
    return response


def get_game_list(types):
    return {}


def game_inform_request_handler(data):
    return game_inform_response(data, data["Session"])


#def update_game(data):
#    return {}


def game_inform_response(data, session):
    if session_valid(session):
        add_game(data)
        message = "Game Inform"
        detail = "Termination successful"
        response = {'Type': 'Success', 'Session': session, 'Message': message, 'Detail': detail}
        return response
    else:
        message = "Authentication Failure"
        detail = "Action may only be performed by authenticated clients"
        response = {'Type': 'Fail', 'Session': session, 'Message': message, 'Detail': detail}
        return response


def add_game(data):
    pass


def sucesss_request_handler(data):
    return success_response(data)


def success_response(data):
    if session_valid(data["Session"]):
        print "Session: " + str(data["Session"])
        print "Player: " + str(data["Player Name"])
        print "Request:" + str(data["Message"])
        print "Success: " + str(data["Detail"])
        response = ""
    else:
        message = "Authentication Failure"
        detail = "Action may only be performed by authenticated clients"
        response = {'Type': 'Fail', 'Session': data["Session"], 'Message': message, 'Detail': detail}
    return response


def fail_request_handler(data):
    return fail_response(data)


def fail_response(data):
    if session_valid(data["Session"]):
        print "Session: " + str(data["Session"])
        print "Player: " + str(data["Player Name"])
        print "Request:" + str(data["Message"])
        print "Fail: " + str(data["Detail"])
        response = ""
    else:
        message = "Authentication Failure"
        detail = "Action may only be performed by authenticated clients"
        response = {'Type': 'Fail', 'Session': data["Session"], 'Message': message, 'Detail': detail}
    return response


def terminate_session_request_handler(data):
    return terminate_response(data["Session"])


def terminate_response(session):
    if session_valid(session):
        if terminate_session(session):
            message = "Session Terminate"
            detail = "Termination successful"
            response = {'Type': 'Success', 'Session': session, 'Message': message, 'Detail': detail}
        else:
            response = error_response(session)
    else:
        message = "Authentication Failure"
        detail = "Action may only be performed by authenticated clients"
        response = {'Type': 'Fail', 'Session': session, 'Message': message, 'Detail': detail}
    return response


def terminate_session(session):
    return True


def error_request_handler(data):
    print data
    return error_response(data)


def error_response(data):
    print data
    return data


def session_valid(session):
    return True


if __name__ == "__main__":
    try:
        import sys

        main(sys.argv[1])
    except:
        main()
    else:
        pass