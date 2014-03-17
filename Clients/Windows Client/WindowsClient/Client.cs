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
        private static HttpClient HTTPGameEngineClient;

        internal static int Session;
        internal static JObject Player;
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
            HTTPGameEngineOnConnect();
        }

        internal static async void HTTPServerSend(JObject data)
        {
            StringContent requestContent = new StringContent(data.ToString());
            Task<HttpResponseMessage> responseTask = HTTPServerClient.PostAsync(HTTPServerURI, requestContent);
            HttpResponseMessage responseMessage = await responseTask;
            HTTPRequestHandler(responseMessage.Content.ReadAsStringAsync());
        }

        private static void HTTPGameEngineConnect(Uri httpGameEngineURI)
        {
            HTTPGameEngineURI = httpGameEngineURI;
            HTTPGameEngineClient = new HttpClient();
            //OnConnect();
        }

        private static void HTTPGameEngineOnConnect()
        {
            JObject messsage = ServerClient.ServerChatRequest(Client.Session, Client.Username,
                ("User: " + Client.Username + " connected"), Client.Status);
            HTTPServerSend(messsage);
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
                else if (responseType.Equals("Server Session Response"))
                {
                    ServerClient.ServerSessionHandler(response);
                }
                else if (responseType.Equals("Game List Response"))
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
                else if (responseType.Equals("Game Session Response"))
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

        internal static JObject ServerErrorRequest(int session, string command, JObject message)
        {
            string serverErrorRequest = "{'Type': 'Error', 'Session': " + session + ", 'Command': '" + command + "',  'Message': '" + message + "', 'Source': '" + Source + "' }";
            return JObject.Parse(serverErrorRequest);
        }

        internal static JObject ServerSucessRequest(int session, string command, JObject message)
        {
            string serverSucessRequest = "{'Type': 'Success', 'Session': " + session + ", 'Command': '" + command + "', 'Message': '" + message + "', 'Source': '" + Source + "' }";
            return JObject.Parse(serverSucessRequest);
        }

        internal static JObject ServerFailRequest(int session, string command, JObject message)
        {
            string serverFailRequest = "{'Type: 'Fail', 'Session': " + session + ", 'Command': '" + command + "', 'Message': '" + message + "', 'Source': '" + Source + "' }";
            return JObject.Parse(serverFailRequest);
        }

        internal static JObject ServerTerminateSessionRequest(int session)
        {
            string serverTerminateSessionRequest = "{'Type': 'Terminate Session', 'Session': " + session + ", 'Source': '" + Source + "' }";
            return JObject.Parse(serverTerminateSessionRequest);
        }

        internal static JObject ServerGameListRequest(int session, JObject platform, JObject features)
        {
            string serverGameListRequest = "{'Type': 'Game List Request', 'Session': " + session + ", 'Platform': platform,  'Features': " + features + ", 'Source': '" + Source + "' }";
            return JObject.Parse(serverGameListRequest);
        }

        internal static JObject ServerSessionRequest(int session, JObject username, JObject password)
        {
            string serverSessionRequest = "{'Type': 'Server Session Request', 'Session': " + session + ", 'Username': " + username + ", 'Password': " + password + ", 'Source': '" + Source + "' }";
            return JObject.Parse(serverSessionRequest);
        }

        internal static JObject ServerChatRequest(int session, string username, string message, string status)
        {
            string serverChatRequest = "{'Type': 'Server Chat', 'Session': " + session + ", 'Username': '" + username + "', 'Message': '" + message + "', 'Status': '" + status + "', 'Source': '" + Source + "' }";
            return JObject.Parse(serverChatRequest);
        }

        internal static void ServerChatHandler(JObject response)
        {
            throw new NotImplementedException();
        }

        internal static void ServerSessionHandler(JObject response)
        {
            Client.Session = response["Session"].Value<int>();
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

        internal static JObject GameErrorRequest(int session, string command, JObject message)
        {
            string gameErrorRequest = "{'Type': 'Error', 'Session': " + session + ", 'Command': '" + command + "', 'Message': '" + message + "', 'Source': '" + Source + "' }";
            return JObject.Parse(gameErrorRequest);
        }

        internal static JObject GameSuccessRequest(int session, string command, JObject message)
        {
            string gameSucessRequest = "{'Type': 'Success', 'Session': " + session + ", 'Command': '" + command + "', 'Message': '" + message + "', 'Source': '" + Source + "' }";
            return JObject.Parse(gameSucessRequest);
        }

        internal static JObject GameFailRequest(int session, string command, JObject message)
        {
            string gameFailRequest = "{'Type: 'Fail', 'Session': " + session + ", 'Command': '" + command + "', 'Message': '" + message + "', 'Source': '" + Source + "' }";
            return JObject.Parse(gameFailRequest);
        }

        internal static JObject GameTerminateRequest(int session)
        {
            string gameTerminateRequest = "{'Type': 'Terminate Game', 'Session': " + session + ", 'Source': '" + Source + "' }";
            return JObject.Parse(gameTerminateRequest);
        }

        internal static JObject GameUpdateRequest(int session)
        {
            string gameUpdateRequest = "{'Type': 'Game Update Request', 'Session': " + session + ", 'Source': '" + Source + "' }";
            return JObject.Parse(gameUpdateRequest);
        }

        internal static JObject GameCommandRequest(int session, string command)
        {
            string gameCommandRequest = "{'Type': 'Game Command', 'Session': " + session + ", 'Command': '" + command + "', 'Source': '" + Source + "' }";
            return JObject.Parse(gameCommandRequest);
        }

        internal static JObject GameSessionRequest(int session, JObject username, JObject password)
        {
            string gameSessionRequest = "{'Type': 'Game Session Request', 'Session': " + session + ", 'Username': " + username + ", 'Source': '" + Source + "' }";
            return JObject.Parse(gameSessionRequest);
        }

        internal static JObject GameChatRequest(int session, string playerName, string message, string status)
        {
            string gameChatRequest = "{'Type': 'Game Chat', 'Session': " + session + ", 'PlayerName': '" + playerName + "', 'Message': '" + message + "', 'Status': " + status + ", 'Source': '" + Source + "' }";
            return JObject.Parse(gameChatRequest);
        }

        internal static void GameChatHandler(JObject response)
        {
            throw new NotImplementedException();
        }

        internal static void GameSessionHandler(JObject response)
        {
            Client.Player = response["Player"].Value<JObject>();
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