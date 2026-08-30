using System.Collections;
using UnityEngine;
using UnityEngine.Networking;

namespace GreenMachine.Data
{
    public sealed class LocalApiClient : MonoBehaviour
    {
        [SerializeField] private string baseUrl = "http://127.0.0.1:8788";

        public IEnumerator GetMarketOverview(System.Action<string> onSuccess, System.Action<string> onFailure)
        {
            using UnityWebRequest request = UnityWebRequest.Get($"{baseUrl}/market/overview");
            request.SetRequestHeader("X-Green-Machine-Token", EnvironmentToken());
            yield return request.SendWebRequest();
            if (request.result == UnityWebRequest.Result.Success) onSuccess?.Invoke(request.downloadHandler.text);
            else onFailure?.Invoke(request.error);
        }

        public IEnumerator GetWorldToday(System.Action<string> onSuccess, System.Action<string> onFailure)
        {
            using UnityWebRequest request = UnityWebRequest.Get($"{baseUrl}/world/today");
            request.SetRequestHeader("X-Green-Machine-Token", EnvironmentToken());
            yield return request.SendWebRequest();
            if (request.result == UnityWebRequest.Result.Success) onSuccess?.Invoke(request.downloadHandler.text);
            else onFailure?.Invoke(request.error);
        }

        public IEnumerator GetSymbolTradePath(string symbol, System.Action<string> onSuccess, System.Action<string> onFailure)
        {
            string encodedSymbol = UnityWebRequest.EscapeURL(symbol.Trim().ToUpperInvariant());
            using UnityWebRequest request = UnityWebRequest.Get($"{baseUrl}/journal/symbol/{encodedSymbol}/trades");
            request.SetRequestHeader("X-Green-Machine-Token", EnvironmentToken());
            yield return request.SendWebRequest();
            if (request.result == UnityWebRequest.Result.Success) onSuccess?.Invoke(request.downloadHandler.text);
            else onFailure?.Invoke(request.error);
        }

        public void OpenSource(string url)
        {
            if (System.Uri.TryCreate(url, System.UriKind.Absolute, out System.Uri source)) Application.OpenURL(source.AbsoluteUri);
        }

        private static string EnvironmentToken()
        {
            return System.Environment.GetEnvironmentVariable("GREEN_MACHINE_API_TOKEN") ?? string.Empty;
        }
    }
}
