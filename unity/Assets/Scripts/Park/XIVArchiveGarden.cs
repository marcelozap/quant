using System;
using System.IO;
using UnityEngine;

namespace GreenMachine.Park
{
    public sealed class XIVArchiveGarden : MonoBehaviour
    {
        [Serializable]
        private sealed class ArchiveDocument
        {
            public ArchiveEntry[] entries;
        }

        [Serializable]
        private sealed class ArchiveEntry
        {
            public string category;
            public string title;
            public string note;
            public string date;
        }

        [SerializeField] private TextMesh display;
        [SerializeField] [Min(1)] private int maxEntries = 4;

        private const string ArchiveFileName = "archive.json";

        private void Start()
        {
            Refresh();
        }

        public void Refresh()
        {
            string path = Path.Combine(Application.persistentDataPath, "XIV", ArchiveFileName);
            if (!File.Exists(path))
            {
                ShowEmptyState();
                return;
            }

            try
            {
                ArchiveDocument document = JsonUtility.FromJson<ArchiveDocument>(File.ReadAllText(path));
                if (document == null || document.entries == null || document.entries.Length == 0)
                {
                    ShowEmptyState();
                    return;
                }

                string text = "ARCHIVE GARDEN\n\n";
                int shown = 0;
                foreach (ArchiveEntry entry in document.entries)
                {
                    if (entry == null || string.IsNullOrWhiteSpace(entry.title)) continue;
                    text += $"{ValueOrFallback(entry.category, "ENTRY").ToUpperInvariant()}  {ValueOrFallback(entry.title, "Untitled")}\n";
                    if (!string.IsNullOrWhiteSpace(entry.date)) text += $"{ValueOrFallback(entry.date, "LOCAL")}\n";
                    text += $"{ValueOrFallback(entry.note, "A remembered thing.")}\n\n";
                    shown++;
                    if (shown >= maxEntries) break;
                }

                if (shown == 0) ShowEmptyState();
                else SetText(text + "LOCAL / EDITABLE");
            }
            catch (IOException)
            {
                ShowUnavailableState();
            }
            catch (UnauthorizedAccessException)
            {
                ShowUnavailableState();
            }
            catch (ArgumentException)
            {
                ShowUnavailableState();
            }
        }

        private void ShowEmptyState()
        {
            SetText("ARCHIVE GARDEN\n\nNO ENTRIES YET\n\nAdd archive.json to the local XIV folder.\n\nLOCAL / EDITABLE");
        }

        private void ShowUnavailableState()
        {
            SetText("ARCHIVE GARDEN\n\nARCHIVE UNAVAILABLE\n\nThe world is still playable.\n\nLOCAL / EDITABLE");
        }

        private void SetText(string value)
        {
            if (display != null) display.text = value;
        }

        private static string ValueOrFallback(string value, string fallback)
        {
            return string.IsNullOrWhiteSpace(value) ? fallback : value.Replace('\n', ' ').Replace('\r', ' ');
        }
    }
}
