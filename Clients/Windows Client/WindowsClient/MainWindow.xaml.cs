using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Configuration;
using System.Net.WebSockets;
using System.Security.Policy;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;
using System.Net.Http;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace WindowsClient
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
            Client.Setup("Platform",new JObject());
            Client.Account("username", "password");

            string serverAddressString = "http:\\\\localhost";
            UriBuilder uriBuilder = new UriBuilder(serverAddressString);
            uriBuilder.Port = 5500;
            Client.HTTPServerConnect(uriBuilder.Uri);
        }

        private void testServer()
        {
            List<string> testMessages = new List<string>();
            testMessages.Add("{ \"Session\": 123, \"Type\": \"Error\", \"Message\": \"Test\",\"Detail\": \"\"}");
            testMessages.Add("{ \"Session\": 123, \"Type\": \"Success\", \"Message\": \"Test\",\"Detail\": \"\"}");
            testMessages.Add("{ \"Session\": 123, \"Type\": \"Fail\", \"Message\": \"Test\",\"Detail\": \"\"}");
            testMessages.Add("{ \"Session\": 123, \"Type\": \"Terminate Session\"}");
            //testMessages.Add(
            //    "{\"Type\": \"Game Inform\", \"Session\": 123,\"Title\": \"Game 1\",\"Network\": {\"IP Address\": \"127.0.0.1\",\"URL\": \"localhost\",\"Communication\": \"HTTP\",\"Client Type\":  [ ]},\"Parameters\": {\"Minimum Players\": 2,\"Maximum Players\": 8,\"Current Players\": 4}}"
            //);
            testMessages.Add("{\"Type\": \"Game List Request\",\"Session\": 123,\"Device\": \"iPhone\",\"Client Type\": []}");
            testMessages.Add("{\"Type\": \"Server Session Request\",\"Username\": \"user\",\"Password\": \"password hash\", \"Session\": 123}");
            testMessages.Add("{\"Type\": \"Chat\",\"Username\": \"user\",\"Message\": \"user message\",\"Status\": \"active\",\"Session\": 123}");

            foreach (var testMessage in testMessages)
            {
                Client.HTTPServerSend(JObject.Parse(testMessage));
            }
        }

        //private void testGameEngine()
        //{
        //    List<string> testMessages = new List<string>();
        //    testMessages.Add("{ \"Session\": 123, \"Player Name\": \"player\", \"Type\": \"Error\", \"Message\": \"Test\", \"Detail\": \"\"}");
        //    testMessages.Add("{ \"Session\": 123, \"Player Name\": \"player\", \"Type\": \"Success\", \"Message\": \"Test\", \"Detail\": \"\"}");
        //    testMessages.Add("{ \"Session\": 123, \"Player Name\": \"player\", \"Type\": \"Fail\", \"Message\": \"Test\", \"Detail\": \"\"}");
        //    testMessages.Add("{ \"Session\": 123, \"Player Name\": \"player\", \"Type\": \"Game Terminate\"}");
        //    testMessages.Add("{ \"Session\": 123, \"Player Name\": \"player\", \"Type\": \"Game Command\", \"Command\":{}}");
        //    testMessages.Add("{ \"Session\": 123, \"Player Name\": \"player\", \"Type\": \"Game Update\"}");
        //    testMessages.Add("{ \"Type\": \"Game Session Request\",\"Username\": \"user\",\"Password\": \"password hash\", \"Session\": 123}");
        //    testMessages.Add("{ \"Type\": \"Chat\", \"Player Name\": \"player\", \"Username\": \"user\",\"Message\": \"user message\",\"Status\": \"active\",\"Session\": 123}");

        //    foreach (var testMessage in testMessages)
        //    {
        //        gameEngineClient.Request(JObject.Parse(testMessage));
        //    }
        //}
    }
    /*
    public class HTTPServerClient
    {



        public HTTPServerClient()
        {
            string serverAddressString = "http:\\\\localhost";
            UriBuilder uriBuilder = new UriBuilder(serverAddressString);
            uriBuilder.Port = 5500;
            serverAddress = uriBuilder.Uri;
            serverClient = new HttpClient();
        }

        public async void Request(JObject messageJsonObject)
        {
            //MessageBox.Show(messageJsonObject.ToString());
            JObject response = await makeRequest(messageJsonObject);
            procecesResponse(response);

        }

        private void procecesResponse(JObject response)
        {
            //MessageBox.Show(response.ToString());
        }


    }

    public class HTTPSGameEngineClient
    {

        private Uri gameEngineAddress;
        private HttpClient gameEngineClient;

        public HTTPSGameEngineClient()
        {
            string serverAddressString = "http:\\\\localhost";
            UriBuilder uriBuilder = new UriBuilder(serverAddressString);
            uriBuilder.Port = 6500;
            gameEngineAddress = uriBuilder.Uri;
            gameEngineClient = new HttpClient();
        }

        public async void Request(JObject messageJsonObject)
        {
            //MessageBox.Show(messageJsonObject.ToString());
            JObject response = await makeRequest(messageJsonObject);
            procecesResponse(response);

        }

        private void procecesResponse(JObject response)
        {
            //MessageBox.Show(response.ToString());
        }

        private async Task<JObject> makeRequest(JObject messageJsonObject)
        {
            StringContent requestContent = new StringContent(messageJsonObject.ToString());

            Task<HttpResponseMessage> responseTask = gameEngineClient.PostAsync(gameEngineAddress, requestContent);
            HttpResponseMessage responseMessage = await responseTask;

            Task<string> responseStringTask = responseMessage.Content.ReadAsStringAsync();
            string responseString = await responseStringTask;
            JObject responseJObject = JObject.Parse(responseString);

            return responseJObject;
        }
    }

    // Untested, not supported on Windows 7
    //public class WebSocketServerClient
    //{

    //    private Uri serverAddress;
    //    private ClientWebSocket serverClient;

    //    public WebSocketServerClient()
    //    {
    //        string serverAddressString = "ws:\\\\localhost";
    //        UriBuilder uriBuilder = new UriBuilder(serverAddressString);
    //        uriBuilder.Port = 5500;
    //        uriBuilder.Path = "ws";
    //        serverAddress = uriBuilder.Uri;
    //        serverClient = new ClientWebSocket();
    //    }

    //    public async Task Connect()
    //    {
    //        await serverClient.ConnectAsync(serverAddress, CancellationToken.None);
    //        //await Task.WhenAll(Request())
    //        //serverClient.ReceiveAsync()
    //    }

    //    //public async void Request(JObject messageJsonObject)
    //    //{
    //    //    //MessageBox.Show(messageJsonObject.ToString());
    //    //    JObject response = await makeRequest(messageJsonObject);
    //    //    procecesResponse(response);

    //    //}

    //    //private void procecesResponse(JObject response)
    //    //{
    //    //    //MessageBox.Show(response.ToString());
    //    //}

    //    //private async Task<JObject> makeRequest(JObject messageJsonObject)
    //    //{
    //    //    StringContent requestContent = new StringContent(messageJsonObject.ToString());

    //    //    Task<HttpResponseMessage> responseTask = serverClient.PostAsync(serverAddress, requestContent);
    //    //    HttpResponseMessage responseMessage = await responseTask;

    //    //    Task<string> responseStringTask = responseMessage.Content.ReadAsStringAsync();
    //    //    string responseString = await responseStringTask;
    //    //    JObject responseJObject = JObject.Parse(responseString);

    //    //    return responseJObject;
    //    //}
    //}

    class Protocol
    {
        JObject ServerErrorRequest(int session, string command, string message)
        {
            JObject serverErrorRequest = new JObject();
            serverErrorRequest.Add("Type", "Error");
            serverErrorRequest.Add("Session", session);
            serverErrorRequest.Add("Command", command);
            serverErrorRequest.Add("Message", message);
            return serverErrorRequest;
        }

        JObject ServerSucessRequest(int session, string command, string message)
        {
            JObject serverSucessRequest = new JObject();
            serverSucessRequest.Add("Type", "Success");
            serverSucessRequest.Add("Session", session);
            serverSucessRequest.Add("Command", command);
            serverSucessRequest.Add("Message", message);
            return serverSucessRequest;
        }

        JObject ServerFailRequest(int session, string command, string message)
        {
            JObject serverFailRequest = new JObject();
            serverFailRequest.Add("Type", "Fail");
            serverFailRequest.Add("Session", session);
            serverFailRequest.Add("Command", command);
            serverFailRequest.Add("Message", message);
            return serverFailRequest;
        }

        JObject ServerTerminateSessionRequest(int session)
        {
            JObject serverTerminateSessionRequest = new JObject();
            serverTerminateSessionRequest.Add("Type", "Terminate Session");
            serverTerminateSessionRequest.Add("Session", session);
            return serverTerminateSessionRequest;
        }

        JObject ServerGameListRequest(int session, string platform, JObject features)
        {
            JObject serverGameListRequest = new JObject();
            serverGameListRequest.Add("Type", "Game List Request");
            serverGameListRequest.Add("Session", session);
            serverGameListRequest.Add("Platform", platform);
            serverGameListRequest.Add("Features", features);
            return serverGameListRequest;
        }

        JObject ServerSessionRequest(int session, string username, string password)
        {
            JObject serverSessionRequest = new JObject();
            serverSessionRequest.Add("Type", "Server Session Request");
            serverSessionRequest.Add("Session", session);
            serverSessionRequest.Add("Username", username);
            serverSessionRequest.Add("Password", password);
            return serverSessionRequest;
        }

        JObject ServerChatRequest(int session, string username, string message, string status)
        {
            JObject serverChatRequest = new JObject();
            serverChatRequest.Add("Type", "Server Chat");
            serverChatRequest.Add("Session", session);
            serverChatRequest.Add("Username", username);
            serverChatRequest.Add("Message", message);
            serverChatRequest.Add("Status", status);
            return serverChatRequest;
        }
        
        JObject GameErrorRequest(int session, string command, string message)
        {
            JObject gameErrorRequest = new JObject();
            gameErrorRequest.Add("Type", "Error");
            gameErrorRequest.Add("Session", session);
            gameErrorRequest.Add("Command", command);
            gameErrorRequest.Add("Message", message);
            return gameErrorRequest;
        }

        JObject GameSucessRequest(int session, string command, string message)
        {
            JObject gameSucessRequest = new JObject();
            gameSucessRequest.Add("Type", "Success");
            gameSucessRequest.Add("Session", session);
            gameSucessRequest.Add("Command", command);
            gameSucessRequest.Add("Message", message);
            return gameSucessRequest;
        }

        JObject GameFailRequest(int session, string command, string message)
        {
            JObject gameFailRequest = new JObject();
            gameFailRequest.Add("Type", "Fail");
            gameFailRequest.Add("Session", session);
            gameFailRequest.Add("Command", command);
            gameFailRequest.Add("Message", message);
            return gameFailRequest;
        }

        JObject GameTerminateRequest(int session)
        {
            JObject gameTerminateRequest = new JObject();
            gameTerminateRequest.Add("Type", "Terminate Game");
            gameTerminateRequest.Add("Session", session);
            return gameTerminateRequest;
        }

        JObject GameUpdateRequest(int session)
        {
            JObject gameUpdateRequest = new JObject();
            gameUpdateRequest.Add("Type", "Game Update Request");
            gameUpdateRequest.Add("Session", session);
            return gameUpdateRequest;
        }

        JObject GameCommandRequest(int session, JObject command)
        {
            JObject gameCommandRequest = new JObject();
            gameCommandRequest.Add("Type", "Game Command");
            gameCommandRequest.Add("Session", session);
            gameCommandRequest.Add("Command", command);
            return gameCommandRequest;
        }

        JObject GameSessionRequest(int session, string username)
        {
            JObject gameSessionRequest = new JObject();
            gameSessionRequest.Add("Type", "Game Session Request");
            gameSessionRequest.Add("Session", session);
            gameSessionRequest.Add("Username", username);
            return gameSessionRequest;
        }

        JObject GameChatRequest(int session, string playerName, string message, string status)
        {
            JObject gameChatRequest = new JObject();
            gameChatRequest.Add("Type", "Game Chat");
            gameChatRequest.Add("Session", session);
            gameChatRequest.Add("Player Name", playerName);
            gameChatRequest.Add("Message", message);
            gameChatRequest.Add("Status", status);
            return gameChatRequest;
        }
    }*/
}
