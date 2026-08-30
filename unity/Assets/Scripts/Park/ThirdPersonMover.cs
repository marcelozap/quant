using UnityEngine;
using UnityEngine.InputSystem;

namespace GreenMachine.Park
{
    [RequireComponent(typeof(CharacterController))]
    public sealed class ThirdPersonMover : MonoBehaviour
    {
        [SerializeField] private Transform cameraTransform;
        [SerializeField] private float moveSpeed = 5.5f;
        [SerializeField] private float runSpeed = 8f;
        [SerializeField] private float turnSpeed = 12f;
        [SerializeField] private float acceleration = 24f;
        [SerializeField] private float runAcceleration = 32f;
        [SerializeField] private float deceleration = 30f;

        private Vector3 clickDestination;
        private bool hasClickDestination;

        private CharacterController controller;
        private Vector3 velocity;
        private Vector3 planarVelocity;

        public float CurrentSpeed => planarVelocity.magnitude;
        public bool IsRunning { get; private set; }

        private void Awake() => controller = GetComponent<CharacterController>();

        private void Update()
        {
            if (Mouse.current != null && Mouse.current.leftButton.wasPressedThisFrame && TrySetClickDestination())
            {
                hasClickDestination = true;
            }

            Vector2 input = ReadKeyboardInput();
            Vector3 movement = CameraRelativeMovement(input);

            if (input.sqrMagnitude > 0.001f) hasClickDestination = false;
            if (hasClickDestination)
            {
                Vector3 toDestination = clickDestination - transform.position;
                toDestination.y = 0f;
                if (toDestination.magnitude < 0.25f) hasClickDestination = false;
                else movement = toDestination.normalized;
            }

            IsRunning = movement.sqrMagnitude > 0.001f && ReadRunInput();
            float targetSpeed = IsRunning ? runSpeed : moveSpeed;
            Vector3 desiredVelocity = movement * targetSpeed;
            float response = movement.sqrMagnitude > 0.001f
                ? (IsRunning ? runAcceleration : acceleration)
                : deceleration;
            planarVelocity = Vector3.MoveTowards(planarVelocity, desiredVelocity, response * Time.deltaTime);

            if (planarVelocity.sqrMagnitude > 0.001f)
            {
                Vector3 facing = planarVelocity.normalized;
                transform.forward = Vector3.Slerp(transform.forward, facing, turnSpeed * Time.deltaTime);
            }

            velocity.y += Physics.gravity.y * Time.deltaTime;
            if (controller.isGrounded && velocity.y < 0f) velocity.y = -2f;
            controller.Move((planarVelocity + velocity) * Time.deltaTime);
        }

        private bool ReadRunInput()
        {
            return Keyboard.current != null &&
                (Keyboard.current.leftShiftKey.isPressed || Keyboard.current.rightShiftKey.isPressed);
        }

        private bool TrySetClickDestination()
        {
            Camera camera = cameraTransform != null ? cameraTransform.GetComponent<Camera>() : null;
            if (camera == null || Mouse.current == null) return false;

            Ray ray = camera.ScreenPointToRay(Mouse.current.position.ReadValue());
            if (!Physics.Raycast(ray, out RaycastHit hit, 250f)) return false;
            clickDestination = hit.point;
            return true;
        }

        private Vector2 ReadKeyboardInput()
        {
            if (Keyboard.current == null) return Vector2.zero;

            Vector2 input = Vector2.zero;
            if (Keyboard.current.aKey.isPressed || Keyboard.current.leftArrowKey.isPressed) input.x -= 1f;
            if (Keyboard.current.dKey.isPressed || Keyboard.current.rightArrowKey.isPressed) input.x += 1f;
            if (Keyboard.current.sKey.isPressed || Keyboard.current.downArrowKey.isPressed) input.y -= 1f;
            if (Keyboard.current.wKey.isPressed || Keyboard.current.upArrowKey.isPressed) input.y += 1f;
            return Vector2.ClampMagnitude(input, 1f);
        }

        private Vector3 CameraRelativeMovement(Vector2 input)
        {
            if (cameraTransform == null || input.sqrMagnitude <= 0.001f) return Vector3.zero;

            Vector3 forward = Vector3.ProjectOnPlane(cameraTransform.forward, Vector3.up).normalized;
            Vector3 right = Vector3.ProjectOnPlane(cameraTransform.right, Vector3.up).normalized;
            return (forward * input.y + right * input.x).normalized;
        }
    }
}
