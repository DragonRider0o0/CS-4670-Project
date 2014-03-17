var Client = {
    serverWebSocket: null,
    serverURI: "",
    session: 0,
    player: {
        Name: ""
    },
    username: "",
    password: "",
    status: "",
    platform: "",
    features: {},
    gameList: null,
    game: null,

    Setup: function (platform, features) {
        this.platform = platform;
        this.features = features;
    },
    Account: function (username, password) {
        this.username = username;
        this.password = password
    },
    WebsocketRequestHandler: function (evt) {
        Client.ProcessMessage(evt.data)
    },
    WebsocketConnect: function (serverHost, serverPort) {
        this.uri = "ws://" + serverHost + ":" + serverPort + "/ws";
        this.serverWebSocket = new WebSocket(this.uri);
        this.serverWebSocket.onmessage = this.WebsocketRequestHandler;

        this.serverWebSocket.onclose = this.WebsocketOnDisconnect;

        this.serverWebSocket.onopen = this.WebsocketOnConnect;

    },
    WebsocketOnConnect: function (evt) {
        var message;
        message = ServerClient.ServerChatRequest(Client.session, Client.username, ("User: " + Client.username + " connected"), Client.status);
        Client.serverWebSocket.send(message);
    },
    WebsocketOnDisconnect: function (evt) {
    },
    WebSocketSend: function(data)
    {
        this.serverWebSocket.send(data);
    },
    ProcessMessage: function (message) {
		alert(message);
        var response = JSON.parse(message)
        if (response.Source == "Server") {
            if (response.Type == "Server Chat") {
                ServerClient.ServerChatHandler(response);
            }
            else if (response.Type == "Server Session Response") {
                ServerClient.ServerSessionHandler(response);
            }
            else if (response.Type == "Game List Response") {
                ServerClient.ServerGameListHandler(response);
            }
            else if (response.Type == "Success") {
                ServerClient.ServerSuccessHandler(response);
            }
            else if (response.Type == "Fail") {
                ServerClient.ServerFailHandler(response);
            }
            else if (response.Type == "Error") {
                ServerClient.ServerErrorHandler(response);
            }
        }
        else if (response.Source == "Game Engine") {
            if (response.Type == "Game Chat") {
                GameEngineClient.GameChatHandler(response);
            }
            else if (response.Type == "Game Session Response") {
                GameEngineClient.GameSessionHandler(response);
            }
            else if (response.Type == "Game Update") {
                GameEngineClient.GameUpdateHandler(response);
            }
            else if (response.Type == "Success") {
                GameEngineClient.GameSuccessHandler(response);
            }
            else if (response.Type == "Fail") {
                GameEngineClient.GameFailHandler(response);
            }
            else if (response.Type == "Error") {
                GameEngineClient.GameErrorHandler(response);
            }
        }
    }
}
var ServerClient = {
    Source: "Client",
    ServerErrorRequest: function (session, command, message) {
        var serverErrorRequest = {
            Type: "Error",
            Session: session,
            Command: command,
            Message: message,
            Source: this.Source
        };
        return JSON.stringify(serverErrorRequest);
    },
    ServerSucessRequest: function (session, command, message) {
        var serverSucessRequest = {
            Type: "Success",
            Session: session,
            Command: command,
            Message: message,
            Source: this.Source
        };
        return JSON.stringify(serverSucessRequest);
    },
    ServerFailRequest: function (session, command, message) {
        var serverFailRequest = {
            Type: "Fail",
            Session: session,
            Command: command,
            Message: message,
            Source: this.Source
        };
        return JSON.stringify(serverFailRequest);
    },
    ServerTerminateSessionRequest: function (session) {
        var serverTerminateSessionRequest = {
            Type: "Terminate Session",
            Session: session,
            Source: this.Source
        };
        return JSON.stringify(serverTerminateSessionRequest);
    },
    ServerGameListRequest: function (session, platform, features) {
        var serverGameListRequest = {
            Type: "Game List Request",
            Session: session,
            Platform: platform,
            Features: features,
            Source: this.Source
        };
        return JSON.stringify(serverGameListRequest);
    },
    ServerSessionRequest: function (session, username, password) {
        var serverSessionRequest = {
            Type: "Server Session Request",
            Session: session,
            Username: username,
            Password: password,
            Source: this.Source
        };
        return JSON.stringify(serverSessionRequest);
    },
    ServerChatRequest: function (session, username, message, status) {
        var serverChatRequest = {
            Type: "Server Chat",
            Session: session,
            Username: username,
            Message: message,
            Status: status,
            Source: this.Source
        };
        return JSON.stringify(serverChatRequest);
    },
    ServerErrorHandler: function (errorData) {
    },
    ServerSuccessHandler: function (successData) {
    },
    ServerFailHandler: function (failData) {
    },
    ServerGameListHandler: function (gameListData) {
        Client.gameList = gameListData.Games;
    },
    ServerSessionHandler: function (sessionData) {
        Client.session = sessionData.Session;
    },
    ServerChatHandler: function (chatData) {
    }
};
var GameEngineClient = {
    Source: "Client",
    GameErrorRequest: function (session, command, message) {
        var gameErrorRequest =
        {
            Type: "Error",
            Session: session,
            Command: command,
            Message: message,
            Source: this.Source
        };
        return JSON.stringify(gameErrorRequest);
    },
    GameSuccessRequest: function (session, command, message) {
        var gameErrorRequest =
        {
            Type: "Success",
            Session: session,
            Command: command,
            Message: message,
            Source: this.Source
        };
        return JSON.stringify(gameErrorRequest);
    },
    GameFailRequest: function (session, command, message) {
        var gameFailRequest =
        {
            Type: "Fail",
            Session: session,
            Command: command,
            Message: message,
            Source: this.Source
        };
        return JSON.stringify(gameFailRequest);
    },
    GameTerminateRequest: function (session) {
        var gameTerminateRequest = {
            Type: "Terminate Game",
            Session: session,
            Source: this.Source
        };
        return JSON.stringify(gameTerminateRequest);
    },
    GameUpdateRequest: function (session) {
        var gameUpdateRequest = {
            Type: "Game Update Request",
            Session: session,
            Source: this.Source
        };
        return JSON.stringify(gameUpdateRequest);
    },
    GameCommandRequest: function (session, command) {
        var gameCommandRequest = {
            Type: "Game Command",
            Session: session,
            Command: command,
            Source: this.Source
        };
        return JSON.stringify(gameCommandRequest);
    },
    GameSessionRequest: function (session, username) {
        var gameSessionRequest = {
            Type: "Game Session Request",
            Session: session,
            Username: username,
            Source: this.Source
        };
        return JSON.stringify(gameSessionRequest);
    },
    GameChatRequest: function (session, playerName, message, status) {
        var gameChatRequest = {
            Type: "Game Chat",
            Session: session,
            PlayerName: playerName,
            Message: message,
            Status: status,
            Source: this.Source
        };
        return JSON.stringify(gameChatRequest);
    },
    GameErrorHandler: function (errorData) {
    },
    GameSuccessHandler: function (successData) {
    },
    GameFailHandler: function (failData) {
    },
    GameUpdateHandler: function (gameUpdateData) {
        Client.game = gameUpdateData.Update;
    },
    GameSessionHandler: function (sessionData) {
        Client.player = sessionData.Player;
    },
    GameChatHandler: function (chatData) {
    }
};