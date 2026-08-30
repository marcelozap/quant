using System;
using System.Collections;
using System.IO;
using UnityEngine;
using UnityEngine.Networking;

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
        private readonly MaterialPropertyBlock materialProperties = new MaterialPropertyBlock();
        private float currentEnergy;
        private Light[] reactiveLights = System.Array.Empty<Light>();
        private Renderer[] reactiveRenderers = System.Array.Empty<Renderer>();
        private XIVWindMotion[] reactiveMotion = System.Array.Empty<XIVWindMotion>();
        private float[] beatTimes = System.Array.Empty<float>();

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
            ApplyMotionResponse();
            ApplyLightResponse();
        }

        private void Start()
        {
            Light[] allLights = FindObjectsByType<Light>(FindObjectsSortMode.None);
            reactiveLights = System.Array.FindAll(allLights, light =>
                light != null && (light.name.Contains("Glow") || light.name.Contains("Beacon")));
            Renderer[] allRenderers = FindObjectsByType<Renderer>(FindObjectsSortMode.None);
            reactiveRenderers = System.Array.FindAll(allRenderers, renderer =>
                renderer != null && (renderer.name.Contains("Glow") || renderer.name.Contains("Beacon") || renderer.name.Contains("Lantern")));
            reactiveMotion = FindObjectsByType<XIVWindMotion>(FindObjectsSortMode.None);
            foreach (Renderer renderer in reactiveRenderers)
            {
                if (renderer == null || renderer.sharedMaterial == null) continue;
                if (renderer.material.HasProperty("_EmissionColor"))
                {
                    renderer.material.EnableKeyword("_EMISSION");
                }
            }

            string analysisPath = Environment.GetEnvironmentVariable("XIV_AUDIO_ANALYSIS_PATH");
            if (!string.IsNullOrWhiteSpace(analysisPath)) LoadAnalysisFile(analysisPath);

            string audioPath = Environment.GetEnvironmentVariable("XIV_AUDIO_PATH");
            if (!string.IsNullOrWhiteSpace(audioPath)) LoadMusicFile(audioPath);
            else TryLoadLocalAudio();
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

        public void LoadMusicFile(string path)
        {
            if (!string.IsNullOrWhiteSpace(path)) StartCoroutine(LoadMusicFileRoutine(path));
        }

        private void TryLoadLocalAudio()
        {
            string audioDirectory = Path.Combine(Application.persistentDataPath, "XIV", "Audio");
            if (!Directory.Exists(audioDirectory)) return;

            try
            {
                string[] files = Directory.GetFiles(audioDirectory);
                Array.Sort(files, StringComparer.OrdinalIgnoreCase);
                foreach (string file in files)
                {
                    if (!IsSupportedAudioPath(file)) continue;
                    LoadMusicFile(file);
                    return;
                }
            }
            catch (IOException)
            {
                // The world still runs with the fallback atmosphere when the local folder is unavailable.
            }
            catch (UnauthorizedAccessException)
            {
                // The world still runs with the fallback atmosphere when the local folder is unavailable.
            }
        }

        public void SetBeatGrid(float bpm, float offsetSeconds = 0f)
        {
            beatBpm = Mathf.Clamp(bpm, 0f, 300f);
            beatOffsetSeconds = offsetSeconds;
            beatTimes = System.Array.Empty<float>();
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

                beatBpm = Mathf.Clamp(document.bpm, 0f, 300f);
                beatOffsetSeconds = document.beat_times[0];
                beatTimes = (float[])document.beat_times.Clone();
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
            beatTimes = System.Array.Empty<float>();
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

        private IEnumerator LoadMusicFileRoutine(string path)
        {
            if (musicSource == null || !File.Exists(path)) yield break;

            using UnityWebRequest request = UnityWebRequestMultimedia.GetAudioClip(
                new Uri(path).AbsoluteUri,
                AudioTypeFor(path));
            yield return request.SendWebRequest();
            if (request.result != UnityWebRequest.Result.Success) yield break;

            AudioClip clip = DownloadHandlerAudioClip.GetContent(request);
            if (clip != null) SetMusic(clip);
        }

        private static AudioType AudioTypeFor(string path)
        {
            return Path.GetExtension(path).ToLowerInvariant() switch
            {
                ".wav" => AudioType.WAV,
                ".ogg" => AudioType.OGGVORBIS,
                _ => AudioType.MPEG,
            };
        }

        private static bool IsSupportedAudioPath(string path)
        {
            string extension = Path.GetExtension(path).ToLowerInvariant();
            return extension == ".mp3" || extension == ".wav" || extension == ".ogg";
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

            Color emission = color * Mathf.Lerp(0.2f, 1.6f, visualEnergy);
            foreach (Renderer renderer in reactiveRenderers)
            {
                if (renderer == null || renderer.sharedMaterial == null || !renderer.sharedMaterial.HasProperty("_EmissionColor")) continue;
                materialProperties.Clear();
                materialProperties.SetColor("_EmissionColor", emission);
                renderer.SetPropertyBlock(materialProperties);
            }
        }

        private void ApplyMotionResponse()
        {
            float visualEnergy = Mathf.Clamp01(currentEnergy + CurrentBeatPulse * beatPulseStrength);
            foreach (XIVWindMotion motion in reactiveMotion)
            {
                if (motion != null) motion.SetAudioEnergy(visualEnergy);
            }
        }

        private float ReadBeatPulse()
        {
            if (musicSource == null || !musicSource.isPlaying) return 0f;

            if (beatTimes.Length > 0)
            {
                float distanceFromBeat = Mathf.Abs(musicSource.time - beatTimes[ClosestBeatIndex(musicSource.time)]);
                return Mathf.Clamp01(1f - distanceFromBeat / beatPulseWidth);
            }

            if (beatBpm <= 0f) return 0f;

            float beatsSinceOffset = (musicSource.time - beatOffsetSeconds) * beatBpm / 60f;
            float phase = Mathf.Repeat(beatsSinceOffset, 1f);
            float distanceFromBeat = Mathf.Min(phase, 1f - phase);
            return Mathf.Clamp01(1f - distanceFromBeat / beatPulseWidth);
        }

        private int ClosestBeatIndex(float time)
        {
            int low = 0;
            int high = beatTimes.Length - 1;
            while (low <= high)
            {
                int middle = low + (high - low) / 2;
                if (beatTimes[middle] < time) low = middle + 1;
                else if (beatTimes[middle] > time) high = middle - 1;
                else return middle;
            }

            if (low >= beatTimes.Length) return beatTimes.Length - 1;
            if (high < 0) return 0;
            return time - beatTimes[high] <= beatTimes[low] - time ? high : low;
        }
    }
}
