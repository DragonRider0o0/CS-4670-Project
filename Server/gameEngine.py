import tornado.httpserver
import tornado.ioloop
import tornado.web
import json


def main(port=8000):
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
        try:
            #self.write("Welcome to the chatroom\n")
            self.finish()
        except:
            # log error message
            pass

    def post(self, call):
        try:
            data = json.loads(self.request.body)
            messageType = data["Type"]
            if messageType == 'Server Session Inform':
                message = serverSessionInformHandler(data)
            elif messageType == 'Game Session Request':
                message = gameSessionRequestHandler(data)
            elif messageType == 'Game Update Request':
                message = gameUpdateRequestHandler(data)
            elif messageType == 'Game Command':
                message = gameCommandRequestHandler(data)
            elif messageType == 'Terminate Game':
                message = terminateGameRequestHandler(data)
            elif messageType == 'Error':
                message = errorRequestHandler(data)
            else:
                message = errorRequestHandler(data)

            self.write(json.dumps(message))

            self.finish()
        except:
            # log error message
            pass


def serverSessionInformHandler(data):
    return serverSessionInformResponse(data)


def serverSessionInformResponse(data):
    return data


def gameSessionRequestHandler(data):
    credentialsValid = authenticateUser(data["Username"], data["Password"])
    #credentialsValid = True
    sessionID = 0
    response = sessionResponse(credentialsValid, sessionID)
    return response


def gameSessionRequestResponse(credentialsValid, sessionID):
    if credentialsValid:
        message = "Session Request"
        detailMessage = "Authentication successful"
        response = {'Type': 'Success', 'Session': sessionID, 'Message': message, 'Detail': detailMessage}
    else:
        message = "Not authenticated"
        detailMessage = "Authentication unsuccessful - invalid username or password"
        response = {'Type': 'Fail', 'Session': sessionID, 'Message': message, 'Detail': detailMessage}
    return response


def authenticateUser(Username, Password):
    return True


def gameUpdateRequestHandler(data):
    return gameListResponse(data["Client Type"])


def gameUpdateResponse(clientTypes)
    if credentialsValid:
        response = getGameList(clientTypes)
    else:
        message = "Not authenticated"
        detailMessage = "Action may only be performed by authenticated clients"
        response = {'Type': 'Fail', 'Session': sessionID, 'Message': message, 'Detail': detailMessage}
    return response


def gameCommandRequestHandler(data):
    gameInformResponse(data):

    def gameCommandRequestResponse(data):
        if credentialsValid:
            if updateGame(data):
                response = getGameList(clientTypes)
            else:
                response = errorResponse(data)
        else:
            message = "Not authenticated"
            detailMessage = "Action may only be performed by authenticated clients"
            response = {'Type': 'Fail', 'Session': sessionID, 'Message': message, 'Detail': detailMessage}
        return response

    def terminateGameRequestHandler(data):
        terminateResponse(data)

    def terminateGameRequestResponse(session)
        if credentialsValid:
            if terminateSession(session)
            message = "Game Terminate"
            detailMessage = "Termination successful"
            response = {'Type': 'Success', 'Session': sessionID, 'Message': message, 'Detail': detailMessage}
        else:
            response = errorResponse(data)

    else:
    else:


message = "Not authenticated"
detailMessage = "Action may only be performed by authenticated clients"
response = {'Type': 'Fail', 'Session': sessionID, 'Message': message, 'Detail': detailMessage}


def errorRequestHandler(data):
    print data;


if __name__ == "__main__":
    try:
        import sys

        main(sys.argv[1])
    except:
        main()
    else:
        pass