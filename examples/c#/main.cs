using System;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading.Tasks;
using System.Text.Json;
using System.Collections.Generic;


using System.IO;

class Program
{
    static async Task Main(string[] args)
    {
        var url = "https://devtest.newpage.app/graphql/v1/graphql";
        var tokenFilePath = "../../token.json";

        var token = "";
        try
        {
            token = JsonDocument.Parse(await File.ReadAllTextAsync(tokenFilePath))
                .RootElement.GetProperty("id_token")
                .GetString();

            if (string.IsNullOrEmpty(token))
            {
                throw new Exception("Empty token");
            }
        }
        catch (Exception e)
        {
            Console.WriteLine($"Error while reading token: {e.Message}\n\nRun npm start at the root of the project in order to generate the token file.");
            return;
        }

        var query = @"
query MyQuery {
    carrier {
        id
        label
        createdAt
        updatedAt
    }
}
";

        using (var client = new HttpClient())
        {
            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);
            var hashTable = new Dictionary<string, string>{
                {"query", query}
            };
            var content = new StringContent(JsonSerializer.Serialize(hashTable), System.Text.Encoding.UTF8, "application/json");
            var response = await client.PostAsync(url, content);
            var responseString = await response.Content.ReadAsStringAsync();
            var value = JsonSerializer.Deserialize<Dictionary<string, object>>(responseString);
            Console.WriteLine("Response:");
            Console.WriteLine(JsonSerializer.Serialize(value, new JsonSerializerOptions { WriteIndented = true }));
        }
    }
}
