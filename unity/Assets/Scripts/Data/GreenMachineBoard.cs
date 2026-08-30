using System;
using GreenMachine.Park;
using UnityEngine;

namespace GreenMachine.Data
{
    public sealed class GreenMachineBoard : MonoBehaviour
    {
        [Serializable]
        private sealed class TodayPayload
        {
            public string date;
            public TodayRecord daily_review;
            public TodayRecord song_memory;
            public int review_streak;
        }

        [Serializable]
        private sealed class TodayRecord
        {
            public TodayFields payload;
        }

        [Serializable]
        private sealed class TodayFields
        {
            public string focus;
            public string title;
        }

        [SerializeField] private LocalApiClient apiClient;
        [SerializeField] private TextMesh display;
        [SerializeField] [Min(5f)] private float refreshSeconds = 30f;

        private float refreshTimer;

        private void Start()
        {
            ShowOffline("Start the local service to load today's context.");
            Refresh();
        }

        private void Update()
        {
            refreshTimer += Time.deltaTime;
            if (refreshTimer >= refreshSeconds)
            {
                refreshTimer = 0f;
                Refresh();
            }
        }

        public void Refresh()
        {
            refreshTimer = 0f;
            if (apiClient == null)
            {
                ShowOffline("No local adapter is connected.");
                return;
            }

            StartCoroutine(apiClient.GetWorldToday(ShowToday, ShowError));
        }

        private void ShowToday(string json)
        {
            TodayPayload today;
            try
            {
                today = JsonUtility.FromJson<TodayPayload>(json);
            }
            catch (ArgumentException)
            {
                ShowError("The local response could not be read.");
                return;
            }

            if (today == null)
            {
                ShowError("The local response was empty.");
                return;
            }

            string focus = today.daily_review?.payload?.focus;
            string song = today.song_memory?.payload?.title;
            SetText(
                $"GREEN MACHINE\n" +
                $"{today.date ?? "TODAY"}\n\n" +
                $"FOCUS  {ValueOrFallback(focus, "No review yet")}\n" +
                $"SONG   {ValueOrFallback(song, "No song logged")}\n" +
                $"STREAK {today.review_streak}\n\n" +
                "LOCAL / READ ONLY");
        }

        private void ShowError(string message)
        {
            ShowOffline(message);
        }

        private void ShowOffline(string message)
        {
            SetText("GREEN MACHINE\nLOCAL DATA\n\nOFFLINE BY DESIGN\n" + message);
        }

        private void SetText(string value)
        {
            if (display != null) display.text = value;
        }

        private static string ValueOrFallback(string value, string fallback)
        {
            return string.IsNullOrWhiteSpace(value) ? fallback : value;
        }
    }
}
