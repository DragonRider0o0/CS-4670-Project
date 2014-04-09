var Client = {
    serverWebSocket: null,
    serverURI: {ip: "", port: ""},

    gameEngineWebSocket: null,
    gameEngineURI: {ip: "", port: ""},

    sessionNumber: 0,
    player: {},
    playerName: "",
    username: "",
    password: "",
    status: "",
    source: "Client",
    gameList: null,
    game: null,

    Setup: function (username, password) {
        this.username = username;
        this.password = password
    },
    WebsocketRequestHandler: function (evt) {
        Client.ProcessMessage(evt.data)
    },
    ServerWebsocketConnect: function (serverHost, serverPort) {
        var uri = "ws://" + serverHost + ":" + serverPort + "/ws";
        this.serverWebSocket = new WebSocket(uri);
        this.serverWebSocket.onmessage = this.WebsocketRequestHandler;

        this.serverWebSocket.onclose = this.WebsocketOnDisconnect;

        this.serverWebSocket.onopen = this.WebsocketOnConnect;

    },
    GameEngineWebsocketConnect: function (gameEngineHost, gameEnginePort) {
        var uri = "ws://" + gameEngineHost + ":" + gameEnginePort + "/ws";
        this.gameEngineWebSocket = new WebSocket(uri);
        this.gameEngineWebSocket.onmessage = this.WebsocketRequestHandler;

        this.gameEngineWebSocket.onclose = this.WebsocketOnDisconnect;

        this.gameEngineWebSocket.onopen = this.WebsocketOnConnect;

    },

    WebsocketOnConnect: function (evt) {
        //var message;
        //message = ServerClient.ServerChatRequest(Client.sessionNumber, Client.username, ("User: " + Client.username + " connected"), Client.status);
        //Client.serverWebSocket.send(message);
    },
    WebsocketOnDisconnect: function (evt) {
    },
    WebSocketSend: function(data)
    {
        this.serverWebSocket.send(data);
    },
    ProcessMessage: function (message) {
		//alert(message);
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
    ServerSessionRequest: function () {
        var serverSessionRequest = {
            Type: "Server Session Request",
            SessionNumber: Client.sessionNumber,
            Username: Client.username,
            Password: Client.password,
            Source: Client.source
        };
        return JSON.stringify(serverSessionRequest);
    },
    ServerChatRequest: function (message, status) {
        var serverChatRequest = {
            Type: "Server Chat",
            SessionNumber: Client.sessionNumber,
            Username: Client.username,
            Message: message,
            Status: status,
            Source: Client.source
        };
        return JSON.stringify(serverChatRequest);
    },
    ServerGetChatRequest: function () {
        var serverGetChatRequest = {
            Type: "Get Server Chat",
            SessionNumber: Client.sessionNumber,
            Username: Client.username,
            Source: Client.source
        };
        return JSON.stringify(serverGetChatRequest);
    },
    ServerGetGameList: function () {
        var serverGetGameListRequest = {
            Type: "Get Game List",
            SessionNumber: Client.sessionNumber,
            Username: Client.username,
            Source: Client.source
        };
        return JSON.stringify(serverGetGameListRequest);
    },
    ServerTerminateSessionRequest: function () {
        var serverTerminateSessionRequest = {
            Type: "Terminate Session",
            SessionNumber: Client.sessionNumber,
            Username: Client.username,
            Source: Client.source
        };
        return JSON.stringify(serverTerminateSessionRequest);
    },

    ServerSessionHandler: function (response) {
        Client.sessionNumber = response.SessionNumber;
    },
    ServerChatHandler: function (response) {
        var username = response.Username;
        var message = response.Message;
        var status = response.Status;
        var chatText = "(" + status + ") " + username + ": " + message + "\n";
        alert(chatText);
    },
    ServerGameListHandler: function (response) {
        Client.gameList = response.Games;
        alert(JSON.stringify(Client.gameList));

    },
    ServerSuccessHandler: function (response) {
        var message = response.Message;
        var command = response.Command;
        var successText = "Success: " + command + "\n" + message + "\n";
        alert(successText);
    },
    ServerFailHandler: function (response) {
        var message = response.Message;
        var command = response.Command;
        var failText = "Fail: " + command + "\n" + message + "\n";
        alert(failText);
    },
    ServerErrorHandler: function (response) {
        var message = response.Message;
        var command = response.Command;
        var errorText = "Error: " + command + "\n" + message + "\n";
        alert(errorText);
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

var Test =
{
    Run: function()
    {
        Test.Setup();
        setTimeout(this.RunTests, 1000)
    },
    RunTests: function()
    {
        //Test.TestSessionRequest();
        //Test.TestServerChat();
        //Test.TestGetServerChat();
        Test.TestGetGames();
    },

    Setup: function()
    {
        Client.Setup("user", "password");

        Client.serverURI.ip = "127.0.0.1";
        Client.serverURI.port= "5500";
        Client.ServerWebsocketConnect("localhost", "5500");

        Client.gameEngineURI.ip = "127.0.0.1";
        Client.gameEngineURI.port= "6500";
        //Client.GameEngineWebsocketConnect("localhost", "5500");
    },
    TestSessionRequest: function()
    {
        var response = ServerClient.ServerSessionRequest();
        Client.serverWebSocket.send(response);
    },
    TestServerChat: function()
    {
        var response = ServerClient.ServerChatRequest("Test Message", "Testing");
        Client.serverWebSocket.send(response);
    },
    TestGetServerChat: function()
    {
        var response = ServerClient.ServerGetChatRequest();
        Client.serverWebSocket.send(response);
    },
    TestGetGames: function()
    {
        var response = ServerClient.ServerGetGameList();
        Client.serverWebSocket.send(response);
    }


}