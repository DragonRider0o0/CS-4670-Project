using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Linq;
using System.Net.Http;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;
using System.Timers;
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

        internal static ObservableCollection<string> ServerChatMessages = new ObservableCollection<string>();
        internal static ObservableCollection<string> GameChatMessages = new ObservableCollection<string>();

        //internal static event PropertyChangedEventHandler ServerChatMessagesChanged;
        ////private static string _ServerChatMessages = "";

        //public class ServerChatMessages : INotifyPropertyChanged
        //{
        //    private string _text;
        //    public string Text
        //    {
        //        get
        //        {
        //            return _text;
        //        }
        //        set
        //        {
        //            _text = value;
        //            OnPropertyChanged("ServerMessages");
        //        }
        //    }

        //    protected void OnPropertyChanged(string propertyName)
        //    {
        //        if (PropertyChanged != null)
        //        {
        //            PropertyChanged(this, new PropertyChangedEventArgs(propertyName));
        //        }
        //    }
        //    public event PropertyChangedEventHandler PropertyChanged;
        //}
        


        internal static string LastUserServerMessage = "";

        internal static string LastUserGameMessage = "";

        static Client()
        {
            Password = "";
            Username = "";
            PlayerName = "";
            Status = "";
        }

        internal static void SetAccountInformation(string username, string password, string playerName)
        {
            Username = username;
            Password = password;
            PlayerName = playerName;
            Status = "Active";
        }

        internal static void HTTPServerConnect(Uri httpServerUri)
        {
            HTTPServerURI = httpServerUri;
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

        internal static void HTTPGameEngineConnect(Uri httpGameEngineUri)
        {
            HTTPGameEngineURI = httpGameEngineUri;
            HTTPGameEngineClient = new HttpClient();
            HTTPGameEngineOnConnect();
        }

        private static void HTTPGameEngineOnConnect()
        {
            //JObject messsage = GameEngineClient.GameChatRequest(("Player: " + Client.PlayerName + " connected"));
            //HTTPGameEngineSend(messsage);
        }

        internal static async void HTTPGameEngineSend(JObject data)
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
            string serverTerminateSessionRequest = "{'Type': 'Terminate Session', 'SessionNumber': " + Client.SessionNumber + ", 'Username': '" + Client.Username + "', 'Source': '" + Client.Source + "' }";
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

            if(Client.LastUserServerMessage == message)
            {
                return;
            }
            else
            {
                string chatText = "(" + status + ") " + username + ": " + message + "";
                App.Current.Dispatcher.Invoke(() => Client.ServerChatMessages.Add(chatText)) ; 
            }
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
            //MessageBox.Show(successText);
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

        internal static JObject GameSessionRequest()
        {
            string gameSessionRequest = "{'Type': 'Game Session Request', 'SessionNumber': " + Client.SessionNumber + ", 'Username': '" + Client.Username + "', 'PlayerName': '" + Client.PlayerName + "', 'Source': '" + Client.Source + "' }";
            return JObject.Parse(gameSessionRequest);
        }

        internal static JObject GameChatRequest(string message)
        {
            string gameChatRequest = "{'Type': 'Game Chat', 'SessionNumber': " + Client.SessionNumber + ", 'PlayerName': '" + Client.PlayerName + "', 'Message': '" + message + "', 'Status': '" + Client.Status + "', 'Source': '" + Client.Source + "' }";
            return JObject.Parse(gameChatRequest);
        }

        internal static JObject GameChatRequest(string message, string status)
        {
            Client.Status = status;
            string gameChatRequest = "{'Type': 'Game Chat', 'SessionNumber': " + Client.SessionNumber + ", 'PlayerName': '" + Client.PlayerName + "', 'Message': '" + message + "', 'Status': '" + Client.Status + "', 'Source': '" + Client.Source + "' }";
            return JObject.Parse(gameChatRequest);
        }

        internal static JObject GameGetChatRequest()
        {
            string serverChatRequest = "{'Type': 'Get Server Chat', 'SessionNumber': " + Client.SessionNumber + ", 'Username': '" + Client.Username + "', 'Source': '" + Client.Source + "' }";
            return JObject.Parse(serverChatRequest);
        }

        internal static JObject GetGameUpdateRequest()
        {
            string gameUpdateRequest = "{'Type': 'Get Game Update', 'SessionNumber': " + Client.SessionNumber + ", 'PlayerName': '" + Client.PlayerName + "', 'Source': '" + Client.Source + "' }";
            return JObject.Parse(gameUpdateRequest);
        }

        internal static JObject GameCommandRequest(JObject command)
        {
            string gameCommandRequest = "{'Type': 'Game Command', 'SessionNumber': " + Client.SessionNumber + ", 'PlayerName': '" + Client.PlayerName + "',  'Command': '" + command + "', 'Source': '" + Client.Source + "' }";
            return JObject.Parse(gameCommandRequest);
        }

        internal static JObject GameTerminateRequest()
        {
            string gameTerminateRequest = "{'Type': 'Terminate Game', 'SessionNumber': " + Client.SessionNumber + ", 'PlayerName': '" + Client.PlayerName + "',  'Source': '" + Source + "' }";
            return JObject.Parse(gameTerminateRequest);
        }


        internal static void GameSessionHandler(JObject response)
        {
            Client.Player = response["Player"].Value<JObject>();
        }

        internal static void GameChatHandler(JObject response)
        {
            string playerName = response["PlayerName"].Value<string>();
            string message = response["Message"].Value<string>();
            string status = response["Status"].Value<string>();

            if (Client.LastUserGameMessage == message)
            {
                return;
            }
            else
            {
                string chatText = "(" + status + ") " + playerName + ": " + message + "";
                Client.GameChatMessages.Add(chatText); 
            }
        }

        internal static void GameUpdateHandler(JObject response)
        {
            Client.Game = response["Update"].Value<JObject>();
        }

        internal static void GameSuccessHandler(JObject response)
        {
            string message = response["Message"].Value<string>();
            string command = response["Command"].Value<string>();

            string successText = "Success: " + command + "\n" + message + "\n";
            MessageBox.Show(successText);
        }

        internal static void GameFailHandler(JObject response)
        {
            string message = response["Message"].Value<string>();
            string command = response["Command"].Value<string>();

            string failText = "Fail: " + command + "\n" + message + "\n";
            MessageBox.Show(failText);
        }

        internal static void GameErrorHandler(JObject response)
        {
            string message = response["Message"].Value<string>();
            string command = response["Command"].Value<string>();

            string errorText = "Error: " + command + "\n" + message + "\n";
            MessageBox.Show(errorText);
        }
    }

    internal static class Test
    {
        private static Timer serverTestTimer;
        private static Timer gameEngineTestTimer;

        internal static void Run()
        {
            Setup();
            BeginServerTests();
            BeginGameEngineTests();
        }

        private static void BeginServerTests()
        {
            TestServerSessionRequest();
            serverTestTimer = new System.Timers.Timer(1000);
            serverTestTimer.Elapsed += new ElapsedEventHandler(delegate(object sender, ElapsedEventArgs e)
            {
                if (Client.SessionNumber > 0)
                {
                    RunServerTests(); 
                }
                
            });
            serverTestTimer.Enabled = true;
        }

        private static void RunServerTests()
        {
            serverTestTimer.Stop();
            TestServerChat();
            TestGetServerChat();
            TestGetGames();
            TestTerminateServer();
        }

        private static void TestServerSessionRequest()
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

        private static void TestTerminateServer()
        {
            JObject response = ServerClient.ServerTerminateSessionRequest();
            Client.HTTPServerSend(response);
        }

        private static void BeginGameEngineTests()
        {
            TestGameSessionRequest();
            gameEngineTestTimer = new System.Timers.Timer(5000);
            gameEngineTestTimer.Elapsed += new ElapsedEventHandler(delegate(object sender, ElapsedEventArgs e)
            {
                if (Client.SessionNumber > 0)
                {
                    RunGameEngineTests();
                }

            });
            gameEngineTestTimer.Enabled = true;
        }

        private static void RunGameEngineTests()
        {
            gameEngineTestTimer.Stop();

            TestGameEngineChat();
            TestGetGameEngineChat();
            TestGetGameUpdate();
            TestGameCommand();
            TestTerminateGame();
        }

        private static void TestGameSessionRequest()
        {
            JObject response = GameEngineClient.GameSessionRequest();
            Client.HTTPGameEngineSend(response);
        }

        private static void TestGameEngineChat()
        {
            JObject response = GameEngineClient.GameChatRequest("Test Message", "Testing");
            Client.HTTPGameEngineSend(response);
        }

        private static void TestGetGameEngineChat()
        {
            JObject response = GameEngineClient.GameGetChatRequest();
            Client.HTTPGameEngineSend(response);
        }

        private static void TestGetGameUpdate()
        {
            JObject response = GameEngineClient.GetGameUpdateRequest();
            Client.HTTPGameEngineSend(response);
        }

        private static void TestGameCommand()
        {
            JObject command = new JObject();
            JObject response = GameEngineClient.GameCommandRequest(command);
            Client.HTTPGameEngineSend(response);
        }

        private static void TestTerminateGame()
        {
            JObject response = GameEngineClient.GameTerminateRequest();
            Client.HTTPGameEngineSend(response);
        }

        private static void Setup()
        {
            Client.SetAccountInformation("user", "password", "player");

            UriBuilder testServer = new UriBuilder("http:\\\\localhost");
            testServer.Port = 5500;
            UriBuilder testGameEngine = new UriBuilder("http:\\\\localhost");
            testGameEngine.Port = 6500;

            Client.HTTPServerConnect(testServer.Uri);
            Client.HTTPGameEngineConnect(testGameEngine.Uri);
        }
    }
}

//public class UIData : INotifyPropertyChanged
//{
//    // boiler-plate

//    public UIData()
//    {
//        ServerChatMessages = "";
//    }

//    public event PropertyChangedEventHandler PropertyChanged;
//    protected virtual void OnPropertyChanged(string propertyName)
//    {
//        PropertyChangedEventHandler handler = PropertyChanged;
//        if (handler != null) handler(this, new PropertyChangedEventArgs(propertyName));
//    }
//    protected bool SetField<T>(ref T field, T value, string propertyName)
//    {
//        if (EqualityComparer<T>.Default.Equals(field, value)) return false;
//        field = value;
//        OnPropertyChanged(propertyName);
//        return true;
//    }

//    // props
//    private string serverChatMessages;
//    public string ServerChatMessages
//    {
//        get { return serverChatMessages; }
//        set { SetField(ref serverChatMessages, value, "ServerChatMessages"); }
//    }
//}