using System;
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
        [SerializeField] private Transform player;
        [SerializeField] private RoscoCompanion rosco;
        [SerializeField] private XIVAudioAtmosphere atmosphere;
        [SerializeField] [Min(1f)] private float autosaveSeconds = 15f;

        private WalkSessionRecord record;
        private Vector3 previousPlayerPosition;
        private float autosaveTimer;

        public WalkSessionRecord CurrentRecord => record;
        public bool IsComplete => record != null && !string.IsNullOrWhiteSpace(record.completedAtUtc);

        private void Start()
        {
            record = new WalkSessionRecord { startedAtUtc = DateTime.UtcNow.ToString("O") };
            if (player != null) previousPlayerPosition = player.position;
            if (rosco != null) rosco.InterestDiscovered += OnInterestDiscovered;
        }

        private void Update()
        {
            if (record == null) return;

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

        public void SaveNow()
        {
            if (record == null) return;

            string directory = Path.Combine(Application.persistentDataPath, "XIV");
            Directory.CreateDirectory(directory);
            string path = Path.Combine(directory, "walk-session.json");
            File.WriteAllText(path, JsonUtility.ToJson(record, true));
        }

        public void CompleteWalk(string destinationName)
        {
            if (record == null || IsComplete) return;

            record.destinationName = destinationName;
            record.completedAtUtc = DateTime.UtcNow.ToString("O");
            SaveNow();
        }

        private void OnInterestDiscovered(string pointName)
        {
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
    }
}
