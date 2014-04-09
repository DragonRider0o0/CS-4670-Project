using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using Newtonsoft.Json.Linq;

namespace WindowsClient
{
    internal static class Client
    {
        internal static Uri HTTPServerURI;
        internal static HttpClient HTTPServerClient;

        internal static Uri HTTPGameEngineURI;
        internal static HttpClient HTTPGameEngineClient;

        internal static int SessionNumber;
        internal static JObject Player;
        internal static string PlayerName;
        internal static string Username;
        internal static string Password;
        internal static string Status;
        internal static string Source = "Client";
        internal static JArray GameList;
        internal static JObject Game;

        static Client()
        {
            Password = "";
            Username = "";
            Status = "";
        }

        internal static void SetAccountInformation(string username, string password)
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
            //JObject messsage = ServerClient.ServerChatRequest(("User: " + Client.Username + " connected"), Client.Status);
            //HTTPServerSend(messsage);
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
        internal static JObject ServerSessionRequest()
        {
            string serverSessionRequest = "{'Type': 'Server Session Request', 'SessionNumber': " + Client.SessionNumber + ", 'Username': '" + Client.Username + "', 'Password': '" + Client.Password + "', 'Source': '" + Client.Source + "' }";
            JObject response = JObject.Parse(serverSessionRequest);
            return response;
        }

        internal static JObject ServerChatRequest(string message)
        {
            string serverChatRequest = "{'Type': 'Server Chat', 'SessionNumber': " + Client.SessionNumber + ", 'Username': '" + Client.Username + "', 'Message': '" + message + "', 'Status': '" + Client.Status + "', 'Source': '" + Client.Source + "' }";
            return JObject.Parse(serverChatRequest);
        }

        internal static JObject ServerChatRequest(string message, string status)
        {
            Client.Status = status;
            string serverChatRequest = "{'Type': 'Server Chat', 'SessionNumber': " + Client.SessionNumber + ", 'Username': '" + Client.Username + "', 'Message': '" + message + "', 'Status': '" + Client.Status + "', 'Source': '" + Client.Source + "' }";
            return JObject.Parse(serverChatRequest);
        }

        internal static JObject ServerGetChatRequest()
        {
            string serverChatRequest = "{'Type': 'Get Server Chat', 'SessionNumber': " + Client.SessionNumber + ", 'Username': '" + Client.Username + "', 'Source': '" + Client.Source + "' }";
            return JObject.Parse(serverChatRequest);
        }

        internal static JObject ServerGetGameListRequest()
        {
            string serverGameListRequest = "{'Type': 'Get Game List', 'SessionNumber': " + Client.SessionNumber + ", 'Username': '" + Client.Username + "', 'Source': '" + Client.Source + "' }";
            return JObject.Parse(serverGameListRequest);
        }

        internal static JObject ServerTerminateSessionRequest()
        {
            string serverTerminateSessionRequest = "{'Type': 'Terminate Session', 'SessionNumber': " + Client.SessionNumber + ", 'Username': '" + Client.Username + ", 'Source': '" + Client.Source + "' }";
            return JObject.Parse(serverTerminateSessionRequest);
        }



        internal static void ServerSessionHandler(JObject response)
        {
            Client.SessionNumber = response["SessionNumber"].Value<int>();
        }

        internal static void ServerChatHandler(JObject response)
        {
            string username = response["Username"].Value<string>();
            string message = response["Message"].Value<string>();
            string status = response["Status"].Value<string>();
            string chatText = "(" + status + ") " + username + ": " + message + "\n";

            MessageBox.Show(chatText);
        }

        internal static void ServerGameListHandler(JObject response)
        {
            Client.GameList = response["Games"].Value<JArray>();
            MessageBox.Show(Client.GameList.ToString());
        }

        internal static void ServerSuccessHandler(JObject response)
        {
            string message = response["Message"].Value<string>();
            string command = response["Command"].Value<string>();

            string successText = "Success: " + command + "\n" + message + "\n";
            MessageBox.Show(successText);
        }

        internal static void ServerFailHandler(JObject response)
        {
            string message = response["Message"].Value<string>();
            string command = response["Command"].Value<string>();

            string failText = "Fail: " + command + "\n" + message + "\n";
            MessageBox.Show(failText);
        }

        internal static void ServerErrorHandler(JObject response)
        {
            string message = response["Message"].Value<string>();
            string command = response["Command"].Value<string>();

            string errorText = "Error: " + command + "\n" + message + "\n";
            MessageBox.Show(errorText);
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

    internal static class Test
    {
        internal static void Run()
        {
            Setup();
            //TestSessionRequest();
            //TestServerChat();
            //TestGetServerChat();
            TestGetGames();
        }

        private static void TestSessionRequest()
        {
            JObject response = ServerClient.ServerSessionRequest();
            Client.HTTPServerSend(response);
        }

        private static void TestServerChat()
        {
            JObject response = ServerClient.ServerChatRequest("Test Message", "Testing");
            Client.HTTPServerSend(response);
        }

        private static void TestGetServerChat()
        {
            JObject response = ServerClient.ServerGetChatRequest();
            Client.HTTPServerSend(response);
        }

        private static void TestGetGames()
        {
            JObject response = ServerClient.ServerGetGameListRequest();
            Client.HTTPServerSend(response);
        }

        private static void Setup()
        {
            Client.SetAccountInformation("user", "password");

            UriBuilder testServer = new UriBuilder("http:\\\\localhost");
            testServer.Port = 5500;
            UriBuilder testGameEngine = new UriBuilder("http:\\\\localhost");
            testGameEngine.Port = 6500;

            Client.HTTPServerConnect(testServer.Uri);
            //Client.HTTPGameEngineConnect(testGameEngine.Uri);
        }
    }
}