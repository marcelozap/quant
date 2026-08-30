using UnityEngine;

namespace GreenMachine.Park
{
    public sealed class XIVWindMotion : MonoBehaviour
    {
        [SerializeField] [Min(0f)] private float swayAngle = 3f;
        [SerializeField] [Min(0f)] private float swaySpeed = 0.65f;
        [SerializeField] [Range(0f, 0.15f)] private float bobHeight = 0.03f;
        [SerializeField] private float phaseOffset;

        private Vector3 basePosition;
        private Quaternion baseRotation;

        private void Awake()
        {
            basePosition = transform.localPosition;
            baseRotation = transform.localRotation;
        }

        private void Update()
        {
            float phase = Time.time * swaySpeed + phaseOffset;
            transform.localPosition = basePosition + Vector3.up * (Mathf.Sin(phase) * bobHeight);
            transform.localRotation = baseRotation * Quaternion.Euler(
                Mathf.Sin(phase * 0.83f) * swayAngle,
                0f,
                Mathf.Cos(phase * 0.71f) * swayAngle);
        }
    }
}
