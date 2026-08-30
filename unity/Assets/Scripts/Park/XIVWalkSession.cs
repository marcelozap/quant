using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace GreenMachine.Park
{
    [Serializable]
    public sealed class WalkSessionRecord
    {
        public string startedAtUtc;
        public float durationSeconds;
        public float distanceMeters;
        public int pointsDiscovered;
        public float peakAudioEnergy;
        public string lastPointName;
        public string destinationName;
        public string completedAtUtc;
    }

    public sealed class XIVWalkSession : MonoBehaviour
    {
        [Serializable]
        private sealed class WalkHistory
        {
            public List<WalkSessionRecord> walks = new List<WalkSessionRecord>();
        }

        [SerializeField] private Transform player;
        [SerializeField] private RoscoCompanion rosco;
        [SerializeField] private XIVAudioAtmosphere atmosphere;
        [SerializeField] [Min(1f)] private float autosaveSeconds = 15f;

        private WalkSessionRecord record;
        private List<WalkSessionRecord> history = new List<WalkSessionRecord>();
        private Vector3 previousPlayerPosition;
        private float autosaveTimer;

        public event Action<string> WalkCompleted;
        public WalkSessionRecord CurrentRecord => record;
        public bool IsComplete => record != null && !string.IsNullOrWhiteSpace(record.completedAtUtc);
        public int CompletedWalkCount => history.Count;

        private void Awake()
        {
            history = LoadHistory();
        }

        private void Start()
        {
            record = new WalkSessionRecord { startedAtUtc = DateTime.UtcNow.ToString("O") };
            if (player != null) previousPlayerPosition = player.position;
            if (rosco != null) rosco.InterestDiscovered += OnInterestDiscovered;
        }

        private void Update()
        {
            if (record == null || IsComplete) return;

            record.durationSeconds += Time.deltaTime;
            if (player != null)
            {
                Vector3 delta = player.position - previousPlayerPosition;
                delta.y = 0f;
                record.distanceMeters += Mathf.Min(delta.magnitude, 6f);
                previousPlayerPosition = player.position;
            }

            if (atmosphere != null) record.peakAudioEnergy = Mathf.Max(record.peakAudioEnergy, atmosphere.CurrentEnergy);

            autosaveTimer += Time.deltaTime;
            if (autosaveTimer >= autosaveSeconds)
            {
                autosaveTimer = 0f;
                SaveNow();
            }
        }

        public bool SaveNow()
        {
            if (record == null) return false;

            try
            {
                string directory = SaveDirectoryPath;
                Directory.CreateDirectory(directory);
                string path = Path.Combine(directory, "walk-session.json");
                WriteAtomically(path, JsonUtility.ToJson(record, true));
                return true;
            }
            catch (IOException)
            {
                return false;
            }
            catch (UnauthorizedAccessException)
            {
                return false;
            }
            catch (ArgumentException)
            {
                return false;
            }
        }

        public bool CompleteWalk(string destinationName)
        {
            if (record == null || IsComplete) return false;

            string previousDestination = record.destinationName;
            string previousCompletion = record.completedAtUtc;
            record.destinationName = destinationName;
            record.completedAtUtc = DateTime.UtcNow.ToString("O");
            if (!SaveNow())
            {
                record.destinationName = previousDestination;
                record.completedAtUtc = previousCompletion;
                return false;
            }

            AppendCompletedWalk();
            WalkCompleted?.Invoke(destinationName);
            return true;
        }

        private void AppendCompletedWalk()
        {
            WalkSessionRecord snapshot = JsonUtility.FromJson<WalkSessionRecord>(JsonUtility.ToJson(record));
            history.Add(snapshot);

            try
            {
                Directory.CreateDirectory(SaveDirectoryPath);
                WriteAtomically(
                    Path.Combine(SaveDirectoryPath, "walk-history.json"),
                    JsonUtility.ToJson(new WalkHistory { walks = history }, true));
            }
            catch (IOException)
            {
                // The current walk is still saved when history storage is unavailable.
            }
            catch (UnauthorizedAccessException)
            {
                // The current walk is still saved when history storage is unavailable.
            }
        }

        private static void WriteAtomically(string path, string contents)
        {
            string temporaryPath = path + ".tmp";
            try
            {
                File.WriteAllText(temporaryPath, contents);
                if (File.Exists(path)) File.Replace(temporaryPath, path, null);
                else File.Move(temporaryPath, path);
            }
            finally
            {
                if (File.Exists(temporaryPath)) File.Delete(temporaryPath);
            }
        }

        private static List<WalkSessionRecord> LoadHistory()
        {
            string path = Path.Combine(SaveDirectoryPath, "walk-history.json");
            if (!File.Exists(path)) return new List<WalkSessionRecord>();

            try
            {
                WalkHistory saved = JsonUtility.FromJson<WalkHistory>(File.ReadAllText(path));
                return saved?.walks ?? new List<WalkSessionRecord>();
            }
            catch (IOException)
            {
                return new List<WalkSessionRecord>();
            }
            catch (UnauthorizedAccessException)
            {
                return new List<WalkSessionRecord>();
            }
            catch (ArgumentException)
            {
                return new List<WalkSessionRecord>();
            }
        }

        private void OnInterestDiscovered(string pointName)
        {
            if (record == null || IsComplete) return;
            record.pointsDiscovered++;
            record.lastPointName = pointName;
        }

        private void OnApplicationPause(bool paused)
        {
            if (paused) SaveNow();
        }

        private void OnApplicationQuit()
        {
            SaveNow();
        }

        private void OnDestroy()
        {
            if (rosco != null) rosco.InterestDiscovered -= OnInterestDiscovered;
        }

        private static string SaveDirectoryPath => Path.Combine(Application.persistentDataPath, "XIV");
    }
}
