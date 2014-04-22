function signInHandler()
{
    var usernameField = document.getElementById("username");
    var playerNameField = document.getElementById("playerName");
    var passwordField = document.getElementById("password");

    var username = usernameField.value;
    var playerName = playerNameField.value;
    var password = passwordField.value;

    if(username == "" || playerName == "" || password =="")
    {
        return;
    }
    else
    {
        var signInElement = document.getElementById("signIn");
        signInElement.className += " hide";

        var signInElement = document.getElementById("game");
        signInElement.className = "col-lg-7 show";

        Client.SetAccountInformation(username, password, playerName);

        var response = ServerClient.ServerSessionRequest();
        Client.serverWebSocket.send(response);

        var response = GameEngineClient.GameSessionRequest();
        Client.gameEngineWebSocket.send(response);
    }
}

function sendServerChatHandler()
{
    var serverMessageField = document.getElementById("serverMessage");

    var serverMessage = serverMessageField.value;
    var username = Client.username;
    var playerName = Client.playerName;
    var status = Client.status;

    if (serverMessage == "")
    {
        return;
    }
    else
    {
        Client.lastUserServerMessage = serverMessage;
        var chatText = "<p>(" + status + ") Me: " + serverMessage + "</p>";
        Client.serverChatMessages = (chatText) + Client.serverChatMessages;
        serverChatBox = document.getElementById("serverChatBox");
        serverChatBox.innerHTML = Client.serverChatMessages;

        var response = ServerClient.ServerChatRequest(serverMessage, status);
        Client.serverWebSocket.send(response);
    }
}

function sendGameEngineChatHandler()
{
    var gameMessageField = document.getElementById("gameMessage");

    var gameMessage = gameMessageField.value;
    var username = Client.username;
    var playerName = Client.playerName;
    var status = Client.status;
    if (gameMessage == "")
    {
        return;
    }
    else
    {
        Client.lastUserGameMessage = gameMessage;

        var chatText = "<p>(" + status + ") Me: " + gameMessage + "</p>";
        Client.gameChatMessages = (chatText) + Client.gameChatMessages;
        gameChatBox = document.getElementById("gameChatBox");
        gameChatBox.innerHTML = Client.gameChatMessages;

        var response = GameEngineClient.GameChatRequest(gameMessage, status);
        Client.gameEngineWebSocket.send(response);
    }
}


function Setup()
{
    Client.serverURI.ip = "127.0.0.1";
    Client.serverURI.port= "5500";
    Client.ServerWebsocketConnect("localhost", "5500");

    Client.gameEngineURI.ip = "127.0.0.1";
    Client.gameEngineURI.port= "6500";
    Client.GameEngineWebsocketConnect("localhost", "6500");
}



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

    serverChatMessages: "",
    lastUserServerMessage: "",

     gameChatMessages: "",
     lastUserGameMessage: "",

    SetAccountInformation: function (username, password, playerName) {
        this.username = username;
        this.password = password;
        this.playerName = playerName;
        this.status = "Active";
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
        if(Client.lastUserServerMessage == message)
        {
            return
        }
        else
        {
            var chatText = "<p>(" + status + ") " + username + ": " + message + "</p>";
            Client.serverChatMessages = (chatText) + Client.serverChatMessages;
            serverChatBox = document.getElementById("serverChatBox");
            serverChatBox.innerHTML = Client.serverChatMessages;
        }

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
    GameSessionRequest: function () {
        var gameSessionRequest = {
            Type: "Game Session Request",
            SessionNumber: Client.sessionNumber,
            Username: Client.username,
            PlayerName: Client.playerName,
            Source: Client.source
        };
        return JSON.stringify(gameSessionRequest);
    },
    GameChatRequest: function (message, status) {
        var gameChatRequest = {
            Type: "Game Chat",
            SessionNumber: Client.sessionNumber,
            PlayerName: Client.playerName,
            Message: message,
            Status: status,
            Source: Client.source
        };
        return JSON.stringify(gameChatRequest);
    },
    GameGetChatRequest: function () {
        var getChatRequest = {
            Type: "Get Chat",
            SessionNumber: Client.sessionNumber,
            PlayerName: Client.playerName,
            Source: Client.source
        };
        return JSON.stringify(getChatRequest);
    },
    GameGetUpdateRequest: function () {
        var getGameUpdateRequest = {
            Type: "Get Game Update",
            SessionNumber: Client.sessionNumber,
            PlayerName: Client.playerName,
            Source: Client.source
        };
        return JSON.stringify(getGameUpdateRequest);
    },
    GameCommandRequest: function (command) {
        var gameCommandRequest = {
            Type: "Game Command",
            SessionNumber: Client.sessionNumber,
            PlayerName: Client.playerName,
            Command: command,
            Source: Client.source
        };
        return JSON.stringify(gameCommandRequest);
    },
    GameTerminateRequest: function () {
        var gameTerminateRequest = {
            Type: "Terminate Game",
            SessionNumber: Client.sessionNumber,
            PlayerName: Client.playerName,
            Source: Client.source
        };
        return JSON.stringify(gameTerminateRequest);
    },

    GameSessionHandler: function (response) {
        Client.player = SessionData.Player;
    },
    GameChatHandler: function (response) {
        var playerName = response.PlayerName;
        var message = response.Message;
        var status = response.Status;
        if(Client.lastUserGameMessage == message)
        {
            return
        }
        else
        {
            var chatText = "<p>(" + status + ") " + playerName + ": " + message + "</p>";
            Client.gameChatMessages = (chatText) + Client.gameChatMessages;
            gameChatBox = document.getElementById("gameChatBox");
            gameChatBox.innerHTML = Client.gameChatMessages;
        }

    },
    GameUpdateHandler: function (response) {
        Client.game = gameUpdateData.Update;
    },
    GameSuccessHandler: function (response) {
        var message = response.Message;
        var command = response.Command;
        var successText = "Success: " + command + "\n" + message + "\n";
        alert(successText);
    },
    GameFailHandler: function (response) {
        var message = response.Message;
        var command = response.Command;
        var failText = "Fail: " + command + "\n" + message + "\n";
        alert(failText);
    },
    GameErrorHandler: function (response) {
        var message = response.Message;
        var command = response.Command;
        var errorText = "Error: " + command + "\n" + message + "\n";
        alert(errorText);
    }
};

var Test =
{
    Run: function()
    {
        Test.Setup();

        setTimeout(
            function()
            {
                //Test.BeginServerTests();
                Test.BeginGameEngineTests();
            },5000);

    },
    BeginServerTests: function()
    {
        Test.TestSessionRequest();
        var timer = setInterval(
            function()
            {
                if(Client.sessionNumber > 0)
                {
                    Test.RunServerTests();
                    clearInterval(timer)
                }
            }
            , 1000);
    },
    RunServerTests: function()
    {
        Test.TestServerChat();
        Test.TestGetServerChat();
        Test.TestGetGames();
        Test.TestTerminateServer();
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
    },
    TestTerminateServer: function()
    {
        var response = ServerClient.ServerTerminateSessionRequest();
        Client.serverWebSocket.send(response);
    },
    BeginGameEngineTests: function()
    {
        Test.TestGameSessionRequest();
        var timer = setInterval(
            function()
            {
                if(Client.sessionNumber > 0)
                {
                    Test.RunGameEngineTests();
                    clearInterval(timer)
                }
            }
            , 5000)
    },
    RunGameEngineTests: function()
    {
        Test.TestGameEngineChat();
        Test.TestGetGameEngineChat();
        Test.TestGetGameUpdate();
        Test.TestGameCommand();
        Test.TestTerminateGame();
    },
    TestGameSessionRequest: function ()
    {
        var response = GameEngineClient.GameSessionRequest();
        Client.gameEngineWebSocket.send(response);
    },
    TestGameEngineChat: function ()
    {
        var message = "Test";
        var status = "Testing";
        var response = GameEngineClient.GameChatRequest(message, status);
        Client.gameEngineWebSocket.send(response);
    },
    TestGetGameEngineChat: function ()
    {
        var response = GameEngineClient.GameGetChatRequest();
        Client.gameEngineWebSocket.send(response);
    },
    TestGetGameUpdate: function ()
    {
        var response = GameEngineClient.GameGetUpdateRequest();
        Client.gameEngineWebSocket.send(response);
    },
    TestGameCommand: function ()
    {
        var command = {};
        var response = GameEngineClient.GameCommandRequest(command);
        Client.gameEngineWebSocket.send(response);
    },
    TestTerminateGame: function ()
    {
        var response = GameEngineClient.GameTerminateRequest();
        Client.gameEngineWebSocket.send(response);
    },
    Setup: function()
    {
        Client.Setup("user", "password");

        Client.serverURI.ip = "127.0.0.1";
        Client.serverURI.port= "5500";
        Client.ServerWebsocketConnect("localhost", "5500");

        Client.gameEngineURI.ip = "127.0.0.1";
        Client.gameEngineURI.port= "6500";
        Client.GameEngineWebsocketConnect("localhost", "5500");
    }
}