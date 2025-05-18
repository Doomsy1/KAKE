using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;

namespace UnityTutorial
{
    public class TCPServerUnity : MonoBehaviour
    {
        [Tooltip("Port to listen on")]
        public int Port = 55000;

        private TcpListener listener;
        private CancellationTokenSource cancellationTokenSource;
        private readonly object queueLock = new object();
        private readonly Queue<string> messageQueue = new Queue<string>();
        private readonly List<Task> clientTasks = new List<Task>();

        void Start()
        {
            try
            {
                // Start listening on all network interfaces
                listener = new TcpListener(IPAddress.Any, Port);
                listener.Start();
                cancellationTokenSource = new CancellationTokenSource();

                // Start accepting clients in a non-blocking way
                _ = AcceptClientsAsync();

                Debug.Log($"[TCPServerUnity] Listening on port {Port}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"[TCPServerUnity] Error starting server: {ex}");
            }
        }

        private async Task AcceptClientsAsync()
        {
            try
            {
                while (!cancellationTokenSource.Token.IsCancellationRequested)
                {
                    Debug.Log("[TCPServerUnity] Waiting for a client to connect...");
                    TcpClient client = await listener.AcceptTcpClientAsync();
                    
                    string clientIdentifier = "Unknown Client";
                    if (client.Client.RemoteEndPoint is IPEndPoint clientEndPoint)
                    {
                        clientIdentifier = clientEndPoint.ToString();
                    }
                    Debug.Log($"[TCPServerUnity] Client connected: {clientIdentifier}");

                    // Start handling this client in a separate task
                    var clientTask = HandleClientAsync(client, clientIdentifier);
                    clientTasks.Add(clientTask);
                }
            }
            catch (Exception ex)
            {
                if (!cancellationTokenSource.Token.IsCancellationRequested)
                {
                    Debug.LogError($"[TCPServerUnity] Error accepting clients: {ex}");
                }
            }
        }

        private async Task HandleClientAsync(TcpClient client, string clientIdentifier)
        {
            try
            {
                using (client)
                using (NetworkStream ns = client.GetStream())
                using (StreamReader reader = new StreamReader(ns, Encoding.UTF8))
                using (StreamWriter writer = new StreamWriter(ns, Encoding.UTF8) { AutoFlush = true })
                {
                    Debug.Log($"[TCPServerUnity] Now handling client: {clientIdentifier}");
                    
                    // Set a read timeout
                    client.ReceiveTimeout = 5000; // 5 seconds
                    
                    while (!cancellationTokenSource.Token.IsCancellationRequested)
                    {
                        try
                        {
                            // Try to read a line with timeout
                            string line = await reader.ReadLineAsync();
                            
                            if (line == null)
                            {
                                Debug.Log($"[TCPServerUnity] Client {clientIdentifier} disconnected");
                                break;
                            }

                            if (!string.IsNullOrEmpty(line))
                            {
                                Debug.Log($"[TCPServerUnity] Received from {clientIdentifier}: '{line}'");
                                
                                // Queue the message
                                lock (queueLock)
                                {
                                    messageQueue.Enqueue(line);
                                }

                                // Send response
                                string responseMessage = $"Server received: {line}\n";
                                await writer.WriteAsync(responseMessage);
                                Debug.Log($"[TCPServerUnity] Sent to {clientIdentifier}: '{responseMessage.TrimEnd('\r', '\n')}'");
                            }
                        }
                        catch (IOException ex)
                        {
                            Debug.LogWarning($"[TCPServerUnity] IO Error with client {clientIdentifier}: {ex.Message}");
                            break;
                        }
                        catch (Exception ex)
                        {
                            Debug.LogError($"[TCPServerUnity] Error handling client {clientIdentifier}: {ex}");
                            break;
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"[TCPServerUnity] Fatal error with client {clientIdentifier}: {ex}");
            }
            finally
            {
                Debug.Log($"[TCPServerUnity] Finished handling client {clientIdentifier}");
            }
        }

        void Update()
        {
            // Process any messages received from clients
            lock (queueLock)
            {
                while (messageQueue.Count > 0)
                {
                    string msg = messageQueue.Dequeue();
                    Debug.Log($"[TCPServerUnity] Processing message: {msg}");
                    // Add your message processing logic here
                }
            }
        }

        void OnApplicationQuit()
        {
            try
            {
                // Signal all tasks to stop
                cancellationTokenSource?.Cancel();

                // Stop the listener
                listener?.Stop();

                // Wait for all client tasks to complete
                Task.WaitAll(clientTasks.ToArray(), 1000); // Wait up to 1 second
            }
            catch (Exception ex)
            {
                Debug.LogError($"[TCPServerUnity] Error during shutdown: {ex}");
            }
        }
    }
} 