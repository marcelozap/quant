using UnityEngine;

namespace GreenMachine.Park
{
    public sealed class XIVWindMotion : MonoBehaviour
    {
        [SerializeField] [Min(0f)] private float swayAngle = 3f;
        [SerializeField] [Min(0f)] private float swaySpeed = 0.65f;
        [SerializeField] [Range(0f, 0.15f)] private float bobHeight = 0.03f;
        [SerializeField] [Range(0f, 1f)] private float audioEnergy;
        [SerializeField] [Range(0f, 1f)] private float audioMotionAmount = 0.35f;
        [SerializeField] private float phaseOffset;

        private Vector3 basePosition;
        private Quaternion baseRotation;

        public void SetAudioEnergy(float value)
        {
            audioEnergy = Mathf.Lerp(audioEnergy, Mathf.Clamp01(value), Time.deltaTime * 5f);
        }

        private void Awake()
        {
            basePosition = transform.localPosition;
            baseRotation = transform.localRotation;
        }

        private void Update()
        {
            float motionScale = 1f + audioEnergy * audioMotionAmount;
            float phase = Time.time * swaySpeed * (1f + audioEnergy * 0.2f) + phaseOffset;
            transform.localPosition = basePosition + Vector3.up * (Mathf.Sin(phase) * bobHeight * motionScale);
            transform.localRotation = baseRotation * Quaternion.Euler(
                Mathf.Sin(phase * 0.83f) * swayAngle * motionScale,
                0f,
                Mathf.Cos(phase * 0.71f) * swayAngle * motionScale);
        }
    }
}
