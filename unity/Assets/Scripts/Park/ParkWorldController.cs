using System;
using System.IO;
using UnityEngine;

namespace GreenMachine.Park
{
    public sealed class ParkWorldController : MonoBehaviour
    {
        [Serializable]
        private sealed class WorldAtmosphereState
        {
            public float parkHour;
        }

        private const string SaveFileName = "world-atmosphere.json";

        [SerializeField] private Light sun;
        [SerializeField] private Material skyMaterial;
        [Range(0f, 24f)] [SerializeField] private float parkHour = 8.5f;
        [SerializeField] private bool reducedMotion;
        [SerializeField] private bool rememberTimeOfDay = true;
        [SerializeField] [Min(5f)] private float saveIntervalSeconds = 30f;

        private readonly Color dawn = new Color(0.98f, 0.55f, 0.45f);
        private readonly Color midday = new Color(0.42f, 0.79f, 0.95f);
        private readonly Color evening = new Color(0.95f, 0.36f, 0.42f);
        private readonly Color night = new Color(0.06f, 0.09f, 0.22f);
        private float saveTimer;

        private void Awake()
        {
            LoadState();
            if (skyMaterial != null) RenderSettings.skybox = skyMaterial;
            ApplyTimeOfDay();
        }

        private void Update()
        {
            if (!reducedMotion) parkHour = (parkHour + Time.deltaTime * 0.03f) % 24f;
            if (rememberTimeOfDay)
            {
                saveTimer += Time.deltaTime;
                if (saveTimer >= saveIntervalSeconds)
                {
                    saveTimer = 0f;
                    SaveState();
                }
            }
            ApplyTimeOfDay();
        }

        public void SetReducedMotion(bool value) => reducedMotion = value;

        public float ParkHour => parkHour;

        public void SetParkHour(float hour)
        {
            parkHour = Mathf.Repeat(hour, 24f);
            ApplyTimeOfDay();
            if (rememberTimeOfDay) SaveState();
        }

        public void SetMarketEnergy(float normalizedEnergy)
        {
            RenderSettings.ambientIntensity = Mathf.Lerp(0.55f, 1.25f, Mathf.Clamp01(normalizedEnergy));
        }

        private void ApplyTimeOfDay()
        {
            Color sky = parkHour switch
            {
                < 8f => Color.Lerp(night, dawn, parkHour / 8f),
                < 16f => Color.Lerp(dawn, midday, (parkHour - 8f) / 8f),
                < 20f => Color.Lerp(midday, evening, (parkHour - 16f) / 4f),
                _ => Color.Lerp(evening, night, (parkHour - 20f) / 4f),
            };
            float daylight = Mathf.Clamp01(Mathf.Sin((parkHour - 6f) / 24f * Mathf.PI * 2f) * 0.5f + 0.5f);
            if (skyMaterial != null)
            {
                if (skyMaterial.HasProperty("_SkyTint")) skyMaterial.SetColor("_SkyTint", sky);
                if (skyMaterial.HasProperty("_Tint")) skyMaterial.SetColor("_Tint", sky);
                if (skyMaterial.HasProperty("_GroundColor")) skyMaterial.SetColor("_GroundColor", Color.Lerp(night, sky, 0.7f));
                if (skyMaterial.HasProperty("_Exposure")) skyMaterial.SetFloat("_Exposure", Mathf.Lerp(0.55f, 1.05f, daylight));
            }

            RenderSettings.fogColor = Color.Lerp(night, sky, 0.62f);
            RenderSettings.fogDensity = Mathf.Lerp(0.018f, 0.006f, daylight);
            if (sun != null)
            {
                sun.transform.rotation = Quaternion.Euler((parkHour - 6f) * 15f, -35f, 0f);
                sun.color = Color.Lerp(Color.white, sky, 0.25f);
                sun.intensity = Mathf.Lerp(0.18f, 1.15f, daylight);
            }
        }

        private void LoadState()
        {
            if (!rememberTimeOfDay) return;

            try
            {
                string path = Path.Combine(SaveDirectoryPath, SaveFileName);
                if (!File.Exists(path)) return;
                WorldAtmosphereState state = JsonUtility.FromJson<WorldAtmosphereState>(File.ReadAllText(path));
                if (state != null && !float.IsNaN(state.parkHour) && !float.IsInfinity(state.parkHour))
                {
                    parkHour = Mathf.Repeat(state.parkHour, 24f);
                }
            }
            catch (IOException)
            {
                // A missing or unreadable atmosphere save falls back to the authored default hour.
            }
            catch (UnauthorizedAccessException)
            {
                // A missing or unreadable atmosphere save falls back to the authored default hour.
            }
            catch (ArgumentException)
            {
                // A malformed atmosphere save falls back to the authored default hour.
            }
        }

        private void SaveState()
        {
            if (!rememberTimeOfDay) return;

            try
            {
                Directory.CreateDirectory(SaveDirectoryPath);
                string path = Path.Combine(SaveDirectoryPath, SaveFileName);
                string temporaryPath = path + ".tmp";
                try
                {
                    File.WriteAllText(temporaryPath, JsonUtility.ToJson(new WorldAtmosphereState { parkHour = parkHour }, true));
                    File.Move(temporaryPath, path, true);
                }
                finally
                {
                    if (File.Exists(temporaryPath)) File.Delete(temporaryPath);
                }
            }
            catch (IOException)
            {
                // The world continues with its in-memory atmosphere when local persistence is unavailable.
            }
            catch (UnauthorizedAccessException)
            {
                // The world continues with its in-memory atmosphere when local persistence is unavailable.
            }
            catch (ArgumentException)
            {
                // The world continues with its in-memory atmosphere when local persistence is unavailable.
            }
        }

        private void OnApplicationPause(bool paused)
        {
            if (paused) SaveState();
        }

        private void OnApplicationQuit()
        {
            SaveState();
        }

        private static string SaveDirectoryPath => Path.Combine(Application.persistentDataPath, "XIV");
    }
}
