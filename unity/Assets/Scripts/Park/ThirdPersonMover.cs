using UnityEngine;

namespace GreenMachine.Park
{
    [RequireComponent(typeof(CharacterController))]
    public sealed class ThirdPersonMover : MonoBehaviour
    {
        [SerializeField] private Transform cameraTransform;
        [SerializeField] private float moveSpeed = 5.5f;
        [SerializeField] private float turnSpeed = 12f;

        private Vector3 clickDestination;
        private bool hasClickDestination;

        private CharacterController controller;
        private Vector3 velocity;

        private void Awake() => controller = GetComponent<CharacterController>();

        private void Update()
        {
            if (Input.GetMouseButtonDown(0) && TrySetClickDestination()) hasClickDestination = true;
            float horizontal = Input.GetAxisRaw("Horizontal");
            float vertical = Input.GetAxisRaw("Vertical");
            Vector3 input = new Vector3(horizontal, 0f, vertical).normalized;
            Vector3 forward = Vector3.ProjectOnPlane(cameraTransform.forward, Vector3.up).normalized;
            Vector3 right = Vector3.ProjectOnPlane(cameraTransform.right, Vector3.up).normalized;
            Vector3 movement = (forward * input.z + right * input.x).normalized;

            if (input.sqrMagnitude > 0.001f) hasClickDestination = false;
            if (hasClickDestination)
            {
                Vector3 toDestination = clickDestination - transform.position;
                toDestination.y = 0f;
                if (toDestination.magnitude < 0.25f) hasClickDestination = false;
                else movement = toDestination.normalized;
            }

            if (movement.sqrMagnitude > 0.001f)
            {
                transform.forward = Vector3.Slerp(transform.forward, movement, turnSpeed * Time.deltaTime);
                controller.Move(movement * moveSpeed * Time.deltaTime);
            }

            velocity.y += Physics.gravity.y * Time.deltaTime;
            if (controller.isGrounded && velocity.y < 0f) velocity.y = -2f;
            controller.Move(velocity * Time.deltaTime);
        }

        private bool TrySetClickDestination()
        {
            Ray ray = cameraTransform.GetComponent<Camera>().ScreenPointToRay(Input.mousePosition);
            if (!Physics.Raycast(ray, out RaycastHit hit, 250f)) return false;
            clickDestination = hit.point;
            return true;
        }
    }
}
