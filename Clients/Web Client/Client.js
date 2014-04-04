var Client = {
    serverWebSocket: null,
    serverURI: "",
    sessionNumber: 0,
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
        message = ServerClient.ServerChatRequest(Client.sessionNumber, Client.username, ("User: " + Client.username + " connected"), Client.status);
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
            if (response.Type == "Server Session") {
                ServerClient.ServerSessionHandler(response);
            }
            else if (response.Type == "Server Chat") {
                ServerClient.ServerChatHandler(response);
            }
            else if (response.Type == "Game List") {
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
            if (response.Type == "Game Session") {
                GameEngineClient.GameSessionHandler(response);
            }
            else if (response.Type == "Game Chat") {
                GameEngineClient.GameChatHandler(response);
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
    ServerSessionRequest: function (sessionNumber, username, password) {
        var serverSessionRequest = {
            Type: "Server Session Request",
            SessionNumber: sessionNumber,
            Username: username,
            Password: password,
            Source: this.Source
        };
        return JSON.stringify(serverSessionRequest);
    },
    ServerChatRequest: function (sessionNumber, username, message, status) {
        var serverChatRequest = {
            Type: "Server Chat",
            SessionNumber: sessionNumber,
            Username: username,
            Message: message,
            Status: status,
            Source: this.Source
        };
        return JSON.stringify(serverChatRequest);
    },
    ServerGetChatRequest: function (sessionNumber, username) {
        var serverGetChatRequest = {
            Type: "Get Server Chat",
            SessionNumber: sessionNumber,
            Username: username,
            Source: this.Source
        };
        return JSON.stringify(serverGetChatRequest);
    },
    ServerGetGameList: function (sessionNumber, username) {
        var serverGetGameListRequest = {
            Type: "Get Game List",
            SessionNumber: sessionNumber,
            Username: username,
            Source: this.Source
        };
        return JSON.stringify(serverGetGameListRequest);
    },
    ServerTerminateSessionRequest: function (sessionNumber, username) {
        var serverTerminateSessionRequest = {
            Type: "Terminate Session",
            SessionNumber: sessionNumber,
            Username: username,
            Source: this.Source
        };
        return JSON.stringify(serverTerminateSessionRequest);
    },

    ServerSessionHandler: function (SessionData) {
        Client.sessionNumber = SessionData.SessionNumber;
    },
    ServerChatHandler: function (chatData) {
    },
    ServerGameListHandler: function (gameListData) {
        Client.gameList = gameListData.Games;
    },
    ServerSuccessHandler: function (successData) {
    },
    ServerFailHandler: function (failData) {
    },
    ServerErrorHandler: function (errorData) {
    }
};
var GameEngineClient = {
    Source: "Client",
    GameSessionRequest: function (sessionNumber, username) {
        var gameSessionRequest = {
            Type: "Game Session Request",
            SessionNumber: sessionNumber,
            Username: username,
            Source: this.Source
        };
        return JSON.stringify(gameSessionRequest);
    },
    GameChatRequest: function (sessionNumber, playerName, message, status) {
        var gameChatRequest = {
            Type: "Game Chat",
            SessionNumber: sessionNumber,
            PlayerName: playerName,
            Message: message,
            Status: status,
            Source: this.Source
        };
        return JSON.stringify(gameChatRequest);
    },
    GameGetChatRequest: function (sessionNumber, playerName) {
        var getChatRequest = {
            Type: "Get Chat",
            SessionNumber: sessionNumber,
            PlayerName: playerName,
            Source: this.Source
        };
        return JSON.stringify(getChatRequest);
    },
    GameGetUpdateRequest: function (sessionNumber, playerName) {
        var getGameUpdateRequest = {
            Type: "Get Game Update",
            SessionNumber: sessionNumber,
            PlayerName: playerName,
            Source: this.Source
        };
        return JSON.stringify(getGameUpdateRequest);
    },
    GameCommandRequest: function (sessionNumber, playerName, command) {
        var gameCommandRequest = {
            Type: "Game Command",
            SessionNumber: sessionNumber,
            PlayerName: playerName,
            Command: command,
            Source: this.Source
        };
        return JSON.stringify(gameCommandRequest);
    },
    GameTerminateRequest: function (sessionNumber, playerName) {
        var gameTerminateRequest = {
            Type: "Terminate Game",
            SessionNumber: sessionNumber,
            PlayerName: playerName,
            Source: this.Source
        };
        return JSON.stringify(gameTerminateRequest);
    },

    GameSessionHandler: function (SessionData) {
        Client.player = SessionData.Player;
    },
    GameChatHandler: function (chatData) {
    },
    GameUpdateHandler: function (gameUpdateData) {
        Client.game = gameUpdateData.Update;
    },
    GameSuccessHandler: function (successData) {
    },
    GameFailHandler: function (failData) {
    },
    GameErrorHandler: function (errorData) {
    }
};