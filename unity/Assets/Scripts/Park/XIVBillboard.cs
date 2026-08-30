using UnityEngine;

namespace GreenMachine.Park
{
    public sealed class XIVBillboard : MonoBehaviour
    {
        [SerializeField] private bool lockVertical = true;

        private Camera targetCamera;

        private void Start()
        {
            targetCamera = Camera.main;
            if (targetCamera == null) targetCamera = FindFirstObjectByType<Camera>();
        }

        private void LateUpdate()
        {
            if (targetCamera == null)
            {
                targetCamera = Camera.main;
                if (targetCamera == null) return;
            }

            Vector3 direction = targetCamera.transform.position - transform.position;
            if (lockVertical) direction.y = 0f;
            if (direction.sqrMagnitude <= 0.001f) return;
            transform.rotation = Quaternion.LookRotation(direction.normalized, Vector3.up);
        }
    }
}
