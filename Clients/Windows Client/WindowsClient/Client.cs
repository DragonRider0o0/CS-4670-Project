using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json.Linq;

namespace WindowsClient
{
    internal static class Client
    {
        private static Uri HTTPServerURI;
        internal static HttpClient HTTPServerClient;

        private static Uri HTTPGameEngineURI;
        internal static HttpClient HTTPGameEngineClient;

        internal static int SessionNumber;
        internal static JObject Player;
        internal static string PlayerName;
        private static string Username;
        private static string Password;
        private static string Status;
        private static string Platform;
        private static JObject Features;
        internal static JObject GameList;
        internal static JObject Game;

        static Client()
        {
            Password = "";
            Username = "";
            Status = "";
            Platform = "Windows";
        }

        internal static void Setup(string platform, JObject features)
        {
            Platform = platform;
            Features = features;
        }

        internal static void Account(string username, string password)
        {
            Username = username;
            Password = password;
        }

        internal static void HTTPServerConnect(Uri httpServerURI)
        {
            HTTPServerURI = httpServerURI;
            HTTPServerClient = new HttpClient();
            HTTPServerOnConnect();
        }

        private static void HTTPServerOnConnect()
        {
            JObject messsage = ServerClient.ServerChatRequest(Client.SessionNumber, Client.Username,
                ("User: " + Client.Username + " connected"), Client.Status);
            HTTPServerSend(messsage);
        }

        internal static async void HTTPServerSend(JObject data)
        {
            StringContent requestContent = new StringContent(data.ToString());
            Task<HttpResponseMessage> responseTask = HTTPServerClient.PostAsync(HTTPServerURI, requestContent);
            HttpResponseMessage responseMessage = await responseTask;
            HTTPRequestHandler(responseMessage.Content.ReadAsStringAsync());
        }

        internal static void HTTPGameEngineConnect(Uri httpServerURI)
        {
            HTTPServerURI = httpServerURI;
            HTTPServerClient = new HttpClient();
            HTTPGameEngineOnConnect();
        }

        private static void HTTPGameEngineOnConnect()
        {
            JObject messsage = GameEngineClient.GameChatRequest(Client.SessionNumber, Client.PlayerName,
                ("Player: " + Client.PlayerName + " connected"), Client.Status);
            HTTPGameEngineSend(messsage);
        }

        private static async void HTTPGameEngineSend(JObject data)
        {
            StringContent requestContent = new StringContent(data.ToString());
            Task<HttpResponseMessage> responseTask = HTTPGameEngineClient.PostAsync(HTTPGameEngineURI, requestContent);
            HttpResponseMessage responseMessage = await responseTask;
            HTTPRequestHandler(responseMessage.Content.ReadAsStringAsync());
        }

        private static async void HTTPRequestHandler(Task<string> evt)
        {
            string responseString = await evt;
            ProcessMessage(responseString);
        }

        private static void ProcessMessage(string message)
        {
            JObject response = JObject.Parse(message);
            string responseSource = response["Source"].ToString();
            string responseType = response["Type"].ToString();
            if (responseSource.Equals("Server"))
            {
                if (responseType.Equals("Server Chat"))
                {
                    ServerClient.ServerChatHandler(response);
                }
                else if (responseType.Equals("Server Session"))
                {
                    ServerClient.ServerSessionHandler(response);
                }
                else if (responseType.Equals("Game List"))
                {
                    ServerClient.ServerGameListHandler(response);
                }
                else if (responseType.Equals("Success"))
                {
                    ServerClient.ServerSuccessHandler(response);
                }
                else if (responseType.Equals("Fail"))
                {
                    ServerClient.ServerFailHandler(response);
                }
                else if (responseType.Equals("Error"))
                {
                    ServerClient.ServerErrorHandler(response);
                }
            }
            else if (responseSource.Equals("Game Engine"))
            {
                if (responseType.Equals("Game Chat"))
                {
                    GameEngineClient.GameChatHandler(response);
                }
                else if (responseType.Equals("Game Session"))
                {
                    GameEngineClient.GameSessionHandler(response);
                }
                else if (responseType.Equals("Game Update"))
                {
                    GameEngineClient.GameUpdateHandler(response);
                }
                else if (responseType.Equals("Success"))
                {
                    GameEngineClient.GameSuccessHandler(response);
                }
                else if (responseType.Equals("Fail"))
                {
                    GameEngineClient.GameFailHandler(response);
                }
                else if (responseType.Equals("Error"))
                {
                    GameEngineClient.GameErrorHandler(response);
                }
            }
        }
    }

    internal static class ServerClient
    {
        private const string Source = "Client";

        internal static JObject ServerSessionRequest(int sessionNumber, string username, string password)
        {
            string serverSessionRequest = "{'Type': 'Server Session Request', 'SessionNumber': " + sessionNumber + ", 'Username': " + username + ", 'Password': " + password + ", 'Source': '" + Source + "' }";
            return JObject.Parse(serverSessionRequest);
        }

        internal static JObject ServerChatRequest(int sessionNumber, string username, string message, string status)
        {
            string serverChatRequest = "{'Type': 'Server Chat', 'SessionNumber': " + sessionNumber + ", 'Username': '" + username + "', 'Message': '" + message + "', 'Status': '" + status + "', 'Source': '" + Source + "' }";
            return JObject.Parse(serverChatRequest);
        }

        internal static JObject ServerGetChatRequest(int sessionNumber, string username)
        {
            string serverChatRequest = "{'Type': 'Get Server Chat', 'SessionNumber': " + sessionNumber + ", 'Username': '" + username + "', 'Source': '" + Source + "' }";
            return JObject.Parse(serverChatRequest);
        }

        internal static JObject ServerGetGameListRequest(int sessionNumber, string username)
        {
            string serverGameListRequest = "{'Type': 'Get Game List', 'SessionNumber': " + sessionNumber + ", 'Username': '" + username + ", 'Source': '" + Source + "' }";
            return JObject.Parse(serverGameListRequest);
        }

        internal static JObject ServerTerminateSessionRequest(int sessionNumber, string username)
        {
            string serverTerminateSessionRequest = "{'Type': 'Terminate Session', 'SessionNumber': " + sessionNumber + ", 'Username': '" + username + ", 'Source': '" + Source + "' }";
            return JObject.Parse(serverTerminateSessionRequest);
        }



        internal static void ServerSessionHandler(JObject response)
        {
            Client.SessionNumber = response["Session"].Value<int>();
        }

        internal static void ServerChatHandler(JObject response)
        {
            throw new NotImplementedException();
        }

        internal static void ServerGameListHandler(JObject response)
        {
            Client.GameList = response["Games"].Value<JObject>();
        }

        internal static void ServerSuccessHandler(JObject response)
        {
            throw new NotImplementedException();
        }

        internal static void ServerFailHandler(JObject response)
        {
            throw new NotImplementedException();
        }

        internal static void ServerErrorHandler(JObject response)
        {
            throw new NotImplementedException();
        }
    }

    internal class GameEngineClient
    {
        private const string Source = "Client";

        internal static JObject GameSessionRequest(int sessionNumber, string username, string password)
        {
            string gameSessionRequest = "{'Type': 'Game Session Request', 'SessionNumber': " + sessionNumber + ", 'Username': " + username + ", 'Source': '" + Source + "' }";
            return JObject.Parse(gameSessionRequest);
        }

        internal static JObject GameChatRequest(int sessionNumber, string playerName, string message, string status)
        {
            string gameChatRequest = "{'Type': 'Game Chat', 'SessionNumber': " + sessionNumber + ", 'PlayerName': '" + playerName + "', 'Message': '" + message + "', 'Status': " + status + ", 'Source': '" + Source + "' }";
            return JObject.Parse(gameChatRequest);
        }

        internal static JObject GetGameUpdateRequest(int sessionNumber, string playerName)
        {
            string gameUpdateRequest = "{'Type': 'Get Game Update', 'SessionNumber': " + sessionNumber + ", 'PlayerName': '" + playerName + "', 'Source': '" + Source + "' }";
            return JObject.Parse(gameUpdateRequest);
        }

        internal static JObject GameCommandRequest(int sessionNumber, string playerName, JObject command)
        {
            string gameCommandRequest = "{'Type': 'Game Command', 'SessionNumber': " + sessionNumber + ", 'PlayerName': '" + playerName + "',  'Command': '" + command + "', 'Source': '" + Source + "' }";
            return JObject.Parse(gameCommandRequest);
        }

        internal static JObject GameTerminateRequest(int sessionNumber, string playerName)
        {
            string gameTerminateRequest = "{'Type': 'Terminate Game', 'SessionNumber': " + sessionNumber + ", 'PlayerName': '" + playerName + "',  'Source': '" + Source + "' }";
            return JObject.Parse(gameTerminateRequest);
        }




        internal static void GameSessionHandler(JObject response)
        {
            Client.Player = response["Player"].Value<JObject>();
        }

        internal static void GameChatHandler(JObject response)
        {
            throw new NotImplementedException();
        }

        internal static void GameUpdateHandler(JObject response)
        {
            Client.Game = response["Update"].Value<JObject>();
        }

        internal static void GameSuccessHandler(JObject response)
        {
            throw new NotImplementedException();
        }

        internal static void GameFailHandler(JObject response)
        {
            throw new NotImplementedException();
        }

        internal static void GameErrorHandler(JObject response)
        {
            throw new NotImplementedException();
        }
    }
}