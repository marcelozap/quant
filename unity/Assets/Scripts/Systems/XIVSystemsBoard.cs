using System;
using System.IO;
using UnityEngine;

namespace GreenMachine.Data
{
    public sealed class XIVSystemsBoard : MonoBehaviour
    {
        [Serializable]
        private sealed class SystemsSnapshot
        {
            public string updated_at;
            public SystemEntry[] systems;
        }

        [Serializable]
        private sealed class SystemEntry
        {
            public string name;
            public string state;
            public string focus;
        }

        [SerializeField] private TextMesh display;
        [SerializeField] [Min(5f)] private float refreshSeconds = 30f;

        private float refreshTimer;

        private void Start()
        {
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
            string path = Path.Combine(Application.persistentDataPath, "XIV", "systems.json");
            if (!File.Exists(path))
            {
                ShowDefault();
                return;
            }

            try
            {
                SystemsSnapshot snapshot = JsonUtility.FromJson<SystemsSnapshot>(File.ReadAllText(path));
                if (snapshot == null || snapshot.systems == null || snapshot.systems.Length == 0)
                {
                    ShowDefault();
                    return;
                }

                string text = $"XIV\nSYSTEMS\n\nUPDATED {ValueOrFallback(snapshot.updated_at, "LOCAL")}\n\n";
                foreach (SystemEntry system in snapshot.systems)
                {
                    if (system == null) continue;
                    text += $"{ValueOrFallback(system.name, "SYSTEM")}  {ValueOrFallback(system.state, "ACTIVE")}\n";
                    text += $"{ValueOrFallback(system.focus, "Personal build")}\n\n";
                }

                text += "LOCAL / EDITABLE";
                SetText(text);
            }
            catch (IOException)
            {
                ShowDefault();
            }
            catch (UnauthorizedAccessException)
            {
                ShowDefault();
            }
            catch (ArgumentException)
            {
                ShowDefault();
            }
        }

        private void ShowDefault()
        {
            SetText(
                "XIV\nSYSTEMS\n\n" +
                "XIV          BUILDING\n" +
                "Personal world\n\n" +
                "MALOSOUND    MUSIC\n" +
                "Audio and performance\n\n" +
                "GREEN MACHINE  DATA\n" +
                "Research and review\n\n" +
                "LOCAL / EDITABLE");
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
