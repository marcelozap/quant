using UnityEngine;

namespace GreenMachine.Park
{
    public sealed class XIVAudioAtmosphere : MonoBehaviour
    {
        [SerializeField] private AudioSource musicSource;
        [SerializeField] private ParkWorldController worldController;
        [SerializeField] [Range(0f, 1f)] private float fallbackEnergy = 0.14f;
        [SerializeField] [Min(0.1f)] private float responseSpeed = 5f;
        [SerializeField] [Min(0.1f)] private float energyScale = 8f;
        [SerializeField] private Color quietLightColor = new Color(0.35f, 0.55f, 0.72f);
        [SerializeField] private Color activeLightColor = new Color(1f, 0.52f, 0.22f);
        [SerializeField] [Min(0f)] private float quietLightIntensity = 1.2f;
        [SerializeField] [Min(0f)] private float activeLightIntensity = 4f;

        private readonly float[] outputSamples = new float[128];
        private float currentEnergy;
        private Light[] reactiveLights = System.Array.Empty<Light>();

        public float CurrentEnergy => currentEnergy;

        private void Update()
        {
            float targetEnergy = musicSource != null && musicSource.isPlaying
                ? ReadMusicEnergy()
                : fallbackEnergy + Mathf.Sin(Time.time * 0.65f) * 0.025f;

            currentEnergy = Mathf.Lerp(currentEnergy, Mathf.Clamp01(targetEnergy), responseSpeed * Time.deltaTime);
            if (worldController != null) worldController.SetMarketEnergy(currentEnergy);
            ApplyLightResponse();
        }

        private void Start()
        {
            Light[] allLights = FindObjectsByType<Light>(FindObjectsSortMode.None);
            reactiveLights = System.Array.FindAll(allLights, light =>
                light != null && (light.name.Contains("Glow") || light.name.Contains("Beacon")));
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
            Color color = Color.Lerp(quietLightColor, activeLightColor, currentEnergy);
            float intensity = Mathf.Lerp(quietLightIntensity, activeLightIntensity, currentEnergy);
            foreach (Light light in reactiveLights)
            {
                if (light == null) continue;
                light.color = color;
                light.intensity = intensity;
            }
        }
    }
}
