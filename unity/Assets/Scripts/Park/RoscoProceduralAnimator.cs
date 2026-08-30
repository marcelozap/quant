using UnityEngine;

namespace GreenMachine.Park
{
    [RequireComponent(typeof(RoscoCompanion))]
    public sealed class RoscoProceduralAnimator : MonoBehaviour
    {
        [SerializeField] private RoscoCompanion companion;
        [SerializeField] private Transform body;
        [SerializeField] private Transform head;
        [SerializeField] private Transform earLeft;
        [SerializeField] private Transform earRight;
        [SerializeField] private Transform frontLegLeft;
        [SerializeField] private Transform frontLegRight;
        [SerializeField] private Transform backLegLeft;
        [SerializeField] private Transform backLegRight;
        [SerializeField] private Transform tail;
        [SerializeField] [Min(0f)] private float legSwingAngle = 22f;
        [SerializeField] [Min(0f)] private float tailWagAngle = 18f;
        [SerializeField] [Min(0f)] private float idleBreathHeight = 0.025f;
        [SerializeField] [Min(0f)] private float celebrationBounce = 0.11f;

        private Vector3 bodyBasePosition;
        private Quaternion headBaseRotation;
        private Quaternion earLeftBaseRotation;
        private Quaternion earRightBaseRotation;
        private Quaternion frontLegLeftBaseRotation;
        private Quaternion frontLegRightBaseRotation;
        private Quaternion backLegLeftBaseRotation;
        private Quaternion backLegRightBaseRotation;
        private Quaternion tailBaseRotation;
        private float gaitPhase;

        private void Awake()
        {
            if (companion == null) companion = GetComponent<RoscoCompanion>();
            bodyBasePosition = body != null ? body.localPosition : Vector3.zero;
            headBaseRotation = head != null ? head.localRotation : Quaternion.identity;
            earLeftBaseRotation = earLeft != null ? earLeft.localRotation : Quaternion.identity;
            earRightBaseRotation = earRight != null ? earRight.localRotation : Quaternion.identity;
            frontLegLeftBaseRotation = frontLegLeft != null ? frontLegLeft.localRotation : Quaternion.identity;
            frontLegRightBaseRotation = frontLegRight != null ? frontLegRight.localRotation : Quaternion.identity;
            backLegLeftBaseRotation = backLegLeft != null ? backLegLeft.localRotation : Quaternion.identity;
            backLegRightBaseRotation = backLegRight != null ? backLegRight.localRotation : Quaternion.identity;
            tailBaseRotation = tail != null ? tail.localRotation : Quaternion.identity;
        }

        private void LateUpdate()
        {
            if (companion == null) return;

            float speed = companion.CurrentSpeed;
            float moving = Mathf.Clamp01(speed / 4.2f);
            bool isMoving = speed > 0.08f;
            if (isMoving) gaitPhase += Time.deltaTime * Mathf.Lerp(3.2f, 8.5f, moving);
            else gaitPhase = Mathf.MoveTowards(gaitPhase, 0f, Time.deltaTime * 2.5f);

            float gait = isMoving ? Mathf.Sin(gaitPhase) * Mathf.Lerp(0.35f, 1f, moving) : 0f;
            float breath = Mathf.Sin(Time.time * 2.2f) * idleBreathHeight;
            float celebration = companion.IsCelebrating ? Mathf.Abs(Mathf.Sin(Time.time * 18f)) * celebrationBounce : 0f;
            float curiousTilt = companion.IsInvestigating ? Mathf.Sin(Time.time * 3.4f) * 7f : 0f;
            float wagSpeed = companion.IsCelebrating ? 15f : Mathf.Lerp(2.5f, 8f, moving);
            float wag = Mathf.Sin(Time.time * wagSpeed) * Mathf.Lerp(5f, tailWagAngle, Mathf.Max(moving, companion.IsCelebrating ? 1f : 0f));

            if (body != null) body.localPosition = bodyBasePosition + Vector3.up * (breath + celebration);
            if (head != null) head.localRotation = headBaseRotation * Quaternion.Euler(curiousTilt - celebration * 22f, 0f, Mathf.Sin(Time.time * 1.7f) * 2f);
            if (earLeft != null) earLeft.localRotation = earLeftBaseRotation * Quaternion.Euler(0f, 0f, curiousTilt * 0.45f + celebration * 18f);
            if (earRight != null) earRight.localRotation = earRightBaseRotation * Quaternion.Euler(0f, 0f, -curiousTilt * 0.45f - celebration * 18f);

            SetLegRotation(frontLegLeft, frontLegLeftBaseRotation, gait * legSwingAngle);
            SetLegRotation(frontLegRight, frontLegRightBaseRotation, -gait * legSwingAngle);
            SetLegRotation(backLegLeft, backLegLeftBaseRotation, -gait * legSwingAngle);
            SetLegRotation(backLegRight, backLegRightBaseRotation, gait * legSwingAngle);

            if (tail != null) tail.localRotation = tailBaseRotation * Quaternion.Euler(0f, wag, 0f);
        }

        private static void SetLegRotation(Transform leg, Quaternion baseRotation, float angle)
        {
            if (leg != null) leg.localRotation = baseRotation * Quaternion.Euler(angle, 0f, 0f);
        }
    }
}
