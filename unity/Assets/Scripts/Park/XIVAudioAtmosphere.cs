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

        private readonly float[] outputSamples = new float[128];
        private float currentEnergy;

        public float CurrentEnergy => currentEnergy;

        private void Update()
        {
            float targetEnergy = musicSource != null && musicSource.isPlaying
                ? ReadMusicEnergy()
                : fallbackEnergy + Mathf.Sin(Time.time * 0.65f) * 0.025f;

            currentEnergy = Mathf.Lerp(currentEnergy, Mathf.Clamp01(targetEnergy), responseSpeed * Time.deltaTime);
            if (worldController != null) worldController.SetMarketEnergy(currentEnergy);
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
    }
}
