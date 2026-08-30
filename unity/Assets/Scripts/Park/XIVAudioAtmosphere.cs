using System;
using System.IO;
using UnityEngine;

namespace GreenMachine.Park
{
    public sealed class XIVAudioAtmosphere : MonoBehaviour
    {
        [Serializable]
        private sealed class AudioAnalysisV1Document
        {
            public float bpm;
            public float[] beat_times;
        }

        [SerializeField] private AudioSource musicSource;
        [SerializeField] private ParkWorldController worldController;
        [SerializeField] [Range(0f, 1f)] private float fallbackEnergy = 0.14f;
        [SerializeField] [Min(0.1f)] private float responseSpeed = 5f;
        [SerializeField] [Min(0.1f)] private float energyScale = 8f;
        [SerializeField] private Color quietLightColor = new Color(0.35f, 0.55f, 0.72f);
        [SerializeField] private Color activeLightColor = new Color(1f, 0.52f, 0.22f);
        [SerializeField] [Min(0f)] private float quietLightIntensity = 1.2f;
        [SerializeField] [Min(0f)] private float activeLightIntensity = 4f;
        [SerializeField] [Range(0f, 300f)] private float beatBpm;
        [SerializeField] private float beatOffsetSeconds;
        [SerializeField] [Range(0.02f, 0.5f)] private float beatPulseWidth = 0.14f;
        [SerializeField] [Range(0f, 1f)] private float beatPulseStrength = 0.35f;

        private readonly float[] outputSamples = new float[128];
        private float currentEnergy;
        private Light[] reactiveLights = System.Array.Empty<Light>();

        public float CurrentEnergy => currentEnergy;
        public float CurrentBeatPulse { get; private set; }
        public bool HasBeatGrid => beatBpm > 0f;

        private void Update()
        {
            float targetEnergy = musicSource != null && musicSource.isPlaying
                ? ReadMusicEnergy()
                : fallbackEnergy + Mathf.Sin(Time.time * 0.65f) * 0.025f;

            currentEnergy = Mathf.Lerp(currentEnergy, Mathf.Clamp01(targetEnergy), responseSpeed * Time.deltaTime);
            CurrentBeatPulse = ReadBeatPulse();
            if (worldController != null) worldController.SetMarketEnergy(currentEnergy);
            ApplyLightResponse();
        }

        private void Start()
        {
            Light[] allLights = FindObjectsByType<Light>(FindObjectsSortMode.None);
            reactiveLights = System.Array.FindAll(allLights, light =>
                light != null && (light.name.Contains("Glow") || light.name.Contains("Beacon")));

            string analysisPath = Environment.GetEnvironmentVariable("XIV_AUDIO_ANALYSIS_PATH");
            if (!string.IsNullOrWhiteSpace(analysisPath)) LoadAnalysisFile(analysisPath);
        }

        public void SetMusic(AudioClip clip)
        {
            if (musicSource == null) return;

            musicSource.clip = clip;
            if (clip == null)
            {
                musicSource.Stop();
                return;
            }

            musicSource.Play();
        }

        public void StopMusic()
        {
            if (musicSource != null) musicSource.Stop();
        }

        public void SetBeatGrid(float bpm, float offsetSeconds = 0f)
        {
            beatBpm = Mathf.Clamp(bpm, 0f, 300f);
            beatOffsetSeconds = offsetSeconds;
        }

        public bool LoadAnalysisFile(string path)
        {
            if (string.IsNullOrWhiteSpace(path)) return false;

            try
            {
                return LoadAnalysisJson(File.ReadAllText(path));
            }
            catch (IOException)
            {
                ClearBeatGrid();
                return false;
            }
            catch (UnauthorizedAccessException)
            {
                ClearBeatGrid();
                return false;
            }
        }

        public bool LoadAnalysisJson(string json)
        {
            if (string.IsNullOrWhiteSpace(json)) return false;

            try
            {
                AudioAnalysisV1Document document = JsonUtility.FromJson<AudioAnalysisV1Document>(json);
                if (document == null || document.bpm < 20f || document.bpm > 300f || document.beat_times == null || document.beat_times.Length == 0)
                {
                    ClearBeatGrid();
                    return false;
                }

                float previous = -1f;
                foreach (float beatTime in document.beat_times)
                {
                    if (beatTime < 0f || beatTime <= previous)
                    {
                        ClearBeatGrid();
                        return false;
                    }
                    previous = beatTime;
                }

                SetBeatGrid(document.bpm, document.beat_times[0]);
                return true;
            }
            catch (ArgumentException)
            {
                ClearBeatGrid();
                return false;
            }
        }

        public void ClearBeatGrid()
        {
            beatBpm = 0f;
            beatOffsetSeconds = 0f;
            CurrentBeatPulse = 0f;
        }

        private float ReadMusicEnergy()
        {
            musicSource.GetOutputData(outputSamples, 0);
            float sumSquares = 0f;
            for (int i = 0; i < outputSamples.Length; i++)
            {
                sumSquares += outputSamples[i] * outputSamples[i];
            }

            return Mathf.Clamp01(Mathf.Sqrt(sumSquares / outputSamples.Length) * energyScale);
        }

        private void ApplyLightResponse()
        {
            float visualEnergy = Mathf.Clamp01(currentEnergy + CurrentBeatPulse * beatPulseStrength);
            Color color = Color.Lerp(quietLightColor, activeLightColor, visualEnergy);
            float intensity = Mathf.Lerp(quietLightIntensity, activeLightIntensity, visualEnergy);
            foreach (Light light in reactiveLights)
            {
                if (light == null) continue;
                light.color = color;
                light.intensity = intensity;
            }
        }

        private float ReadBeatPulse()
        {
            if (musicSource == null || !musicSource.isPlaying || beatBpm <= 0f) return 0f;

            float beatsSinceOffset = (musicSource.time - beatOffsetSeconds) * beatBpm / 60f;
            float phase = Mathf.Repeat(beatsSinceOffset, 1f);
            float distanceFromBeat = Mathf.Min(phase, 1f - phase);
            return Mathf.Clamp01(1f - distanceFromBeat / beatPulseWidth);
        }
    }
}
