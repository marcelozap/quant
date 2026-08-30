using UnityEngine;

namespace GreenMachine.Park
{
    [RequireComponent(typeof(ThirdPersonMover))]
    public sealed class MarceloProceduralAnimator : MonoBehaviour
    {
        [SerializeField] private ThirdPersonMover mover;
        [SerializeField] private Transform body;
        [SerializeField] private Transform head;
        [SerializeField] private Transform armLeft;
        [SerializeField] private Transform armRight;
        [SerializeField] private Transform legLeft;
        [SerializeField] private Transform legRight;
        [SerializeField] private Transform shoulderLeft;
        [SerializeField] private Transform shoulderRight;
        [SerializeField] private Transform scarf;
        [SerializeField] [Min(0f)] private float legSwingAngle = 22f;
        [SerializeField] [Min(0f)] private float armSwingAngle = 16f;
        [SerializeField] [Min(0f)] private float idleBreathHeight = 0.018f;

        private Vector3 bodyBasePosition;
        private Vector3 scarfBasePosition;
        private Quaternion bodyBaseRotation;
        private Quaternion headBaseRotation;
        private Quaternion armLeftBaseRotation;
        private Quaternion armRightBaseRotation;
        private Quaternion legLeftBaseRotation;
        private Quaternion legRightBaseRotation;
        private Quaternion shoulderLeftBaseRotation;
        private Quaternion shoulderRightBaseRotation;
        private Quaternion scarfBaseRotation;
        private float gaitPhase;

        private void Awake()
        {
            if (mover == null) mover = GetComponent<ThirdPersonMover>();
            bodyBasePosition = body != null ? body.localPosition : Vector3.zero;
            bodyBaseRotation = body != null ? body.localRotation : Quaternion.identity;
            scarfBasePosition = scarf != null ? scarf.localPosition : Vector3.zero;
            headBaseRotation = head != null ? head.localRotation : Quaternion.identity;
            armLeftBaseRotation = armLeft != null ? armLeft.localRotation : Quaternion.identity;
            armRightBaseRotation = armRight != null ? armRight.localRotation : Quaternion.identity;
            legLeftBaseRotation = legLeft != null ? legLeft.localRotation : Quaternion.identity;
            legRightBaseRotation = legRight != null ? legRight.localRotation : Quaternion.identity;
            shoulderLeftBaseRotation = shoulderLeft != null ? shoulderLeft.localRotation : Quaternion.identity;
            shoulderRightBaseRotation = shoulderRight != null ? shoulderRight.localRotation : Quaternion.identity;
            scarfBaseRotation = scarf != null ? scarf.localRotation : Quaternion.identity;
        }

        private void LateUpdate()
        {
            if (mover == null) return;

            float moving = Mathf.Clamp01(mover.CurrentSpeed / 5.5f);
            bool isMoving = moving > 0.02f;
            if (isMoving) gaitPhase += Time.deltaTime * Mathf.Lerp(4.5f, 9.5f, moving);
            else gaitPhase = Mathf.MoveTowards(gaitPhase, 0f, Time.deltaTime * 3f);

            float gait = isMoving ? Mathf.Sin(gaitPhase) * moving : 0f;
            float breath = Mathf.Sin(Time.time * 2.1f) * idleBreathHeight * (1f - moving);
            float torsoSway = isMoving ? Mathf.Cos(gaitPhase) * 2.2f * moving : Mathf.Sin(Time.time * 1.3f) * 0.6f;
            float headTurn = isMoving ? Mathf.Sin(gaitPhase * 0.5f) * 2.5f * moving : Mathf.Sin(Time.time * 0.8f) * 1.2f;
            if (body != null) body.localPosition = bodyBasePosition + Vector3.up * breath;
            if (body != null) body.localRotation = bodyBaseRotation * Quaternion.Euler(0f, 0f, torsoSway);
            if (head != null) head.localRotation = headBaseRotation * Quaternion.Euler(0f, headTurn, -torsoSway * 0.3f);

            SetRotation(armLeft, armLeftBaseRotation, -gait * armSwingAngle);
            SetRotation(armRight, armRightBaseRotation, gait * armSwingAngle);
            SetRotation(legLeft, legLeftBaseRotation, gait * legSwingAngle);
            SetRotation(legRight, legRightBaseRotation, -gait * legSwingAngle);
            SetRotation(shoulderLeft, shoulderLeftBaseRotation, -gait * armSwingAngle * 0.25f);
            SetRotation(shoulderRight, shoulderRightBaseRotation, gait * armSwingAngle * 0.25f);

            if (scarf != null)
            {
                float scarfLift = isMoving ? Mathf.Abs(Mathf.Sin(gaitPhase * 0.5f)) * 0.08f : Mathf.Sin(Time.time * 1.7f) * 0.018f;
                scarf.localPosition = scarfBasePosition + Vector3.up * scarfLift;
                scarf.localRotation = scarfBaseRotation * Quaternion.Euler(0f, torsoSway * 0.7f, -gait * 5f);
            }
        }

        private static void SetRotation(Transform target, Quaternion baseRotation, float angle)
        {
            if (target != null) target.localRotation = baseRotation * Quaternion.Euler(angle, 0f, 0f);
        }
    }
}
