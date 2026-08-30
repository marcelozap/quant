using UnityEngine;

namespace GreenMachine.Park
{
    public sealed class ThirdPersonCamera : MonoBehaviour
    {
        [SerializeField] private Transform target;
        [SerializeField] private Vector3 offset = new Vector3(0f, 5.2f, -8.5f);
        [SerializeField] private float smoothTime = 0.12f;

        private Vector3 velocity;

        private void LateUpdate()
        {
            if (target == null) return;
            transform.position = Vector3.SmoothDamp(transform.position, target.position + offset, ref velocity, smoothTime);
            transform.LookAt(target.position + Vector3.up * 1.4f);
        }
    }
}
