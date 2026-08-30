using UnityEngine;
using UnityEngine.InputSystem;

namespace GreenMachine.Park
{
    public sealed class ThirdPersonCamera : MonoBehaviour
    {
        [SerializeField] private Transform target;
        [SerializeField] private Transform secondaryTarget;
        [SerializeField] private Vector3 offset = new Vector3(0f, 5.2f, -8.5f);
        [SerializeField] private float smoothTime = 0.12f;
        [SerializeField] private float lookSensitivity = 0.12f;
        [SerializeField] private float keyboardOrbitSpeed = 90f;
        [SerializeField] private float collisionRadius = 0.25f;
        [SerializeField] private float collisionPadding = 0.18f;
        [SerializeField] private float companionFramingPadding = 0.45f;
        [SerializeField] private LayerMask collisionMask = ~0;

        private Vector3 velocity;
        private float yaw;
        private float pitch;

        public bool FramesSecondaryTarget => secondaryTarget != null;

        private void Start()
        {
            float distance = offset.magnitude;
            if (distance <= 0.01f) distance = 1f;
            Vector3 direction = offset / distance;
            yaw = Mathf.Atan2(direction.x, -direction.z) * Mathf.Rad2Deg;
            pitch = Mathf.Asin(direction.y) * Mathf.Rad2Deg;
        }

        private void LateUpdate()
        {
            if (target == null) return;

            UpdateOrbit();
            Vector3 subjectCenter = target.position;
            float subjectSpread = 0f;
            if (secondaryTarget != null)
            {
                subjectCenter = Vector3.Lerp(target.position, secondaryTarget.position, 0.5f);
                subjectSpread = Vector3.Distance(target.position, secondaryTarget.position);
            }

            Vector3 pivot = subjectCenter + Vector3.up * 1.4f;
            float distance = offset.magnitude + Mathf.Clamp(subjectSpread * companionFramingPadding, 0f, 2.4f);
            Quaternion orbit = Quaternion.Euler(pitch, yaw, 0f);
            Vector3 direction = orbit * Vector3.back;
            Vector3 desiredPosition = pivot + direction * distance;

            if (Physics.SphereCast(
                    pivot,
                    collisionRadius,
                    direction,
                    out RaycastHit hit,
                    distance,
                    collisionMask,
                    QueryTriggerInteraction.Ignore))
            {
                desiredPosition = pivot + direction * Mathf.Max(0.1f, hit.distance - collisionPadding);
            }

            transform.position = Vector3.SmoothDamp(transform.position, desiredPosition, ref velocity, smoothTime);
            transform.LookAt(pivot);
        }

        private void UpdateOrbit()
        {
            if (Mouse.current != null && Mouse.current.rightButton.isPressed)
            {
                Vector2 mouseDelta = Mouse.current.delta.ReadValue();
                yaw += mouseDelta.x * lookSensitivity;
                pitch -= mouseDelta.y * lookSensitivity;
            }

            if (Keyboard.current != null)
            {
                if (Keyboard.current.qKey.isPressed) yaw -= keyboardOrbitSpeed * Time.deltaTime;
                if (Keyboard.current.eKey.isPressed) yaw += keyboardOrbitSpeed * Time.deltaTime;
            }

            pitch = Mathf.Clamp(pitch, -10f, 55f);
        }
    }
}
