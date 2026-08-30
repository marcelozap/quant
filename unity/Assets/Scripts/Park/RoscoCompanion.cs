using System.Collections.Generic;
using UnityEngine;

namespace GreenMachine.Park
{
    public sealed class RoscoCompanion : MonoBehaviour
    {
        private enum CompanionState
        {
            Greeting,
            Follow,
            Wait,
            Investigate,
            Return,
        }

        [SerializeField] private Transform player;
        [SerializeField] private float followDistance = 2.3f;
        [SerializeField] private float followSpeed = 4.2f;
        [SerializeField] private float turnSpeed = 8f;
        [SerializeField] private float stopDistance = 0.35f;
        [SerializeField] private float greetingDuration = 1.4f;
        [SerializeField] private float investigationRadius = 0.4f;
        [SerializeField] private float idleBobHeight = 0.035f;
        [SerializeField] private float idleBobSpeed = 2.4f;
        [SerializeField] private bool inspectNearbyPoints = true;
        [SerializeField] private float interestSearchRadius = 10f;
        [SerializeField] private float interestCooldown = 7f;

        private CompanionState state = CompanionState.Greeting;
        private Vector3 investigationTarget;
        private Vector3 baseScale;
        private float stateTimer;
        private float celebrationTimer;
        private float groundY;
        private float nextInterestCheck;
        private RoscoInterestPoint[] interestPoints = System.Array.Empty<RoscoInterestPoint>();
        private readonly HashSet<RoscoInterestPoint> visitedPoints = new HashSet<RoscoInterestPoint>();

        public event System.Action<string> InterestDiscovered;
        public string CurrentState => state.ToString();

        private void Awake()
        {
            baseScale = transform.localScale;
            stateTimer = greetingDuration;
            groundY = transform.position.y;
        }

        private void Start()
        {
            interestPoints = FindObjectsByType<RoscoInterestPoint>(FindObjectsSortMode.None);
        }

        private void Update()
        {
            if (player == null) return;

            if (state != CompanionState.Investigate || FlatDistance(transform.position, investigationTarget) <= investigationRadius)
            {
                stateTimer -= Time.deltaTime;
            }
            switch (state)
            {
                case CompanionState.Greeting:
                    Face(player.position);
                    if (stateTimer <= 0f) state = CompanionState.Follow;
                    break;
                case CompanionState.Follow:
                    MoveToward(FollowTarget(), followSpeed);
                    CheckForNearbyInterest();
                    break;
                case CompanionState.Wait:
                    Face(player.position);
                    if (stateTimer <= 0f) state = CompanionState.Follow;
                    break;
                case CompanionState.Investigate:
                    MoveToward(investigationTarget, followSpeed * 0.72f);
                    if (FlatDistance(transform.position, investigationTarget) <= investigationRadius)
                    {
                        Face(investigationTarget + player.forward);
                        if (stateTimer <= 0f) state = CompanionState.Return;
                    }
                    break;
                case CompanionState.Return:
                    MoveToward(FollowTarget(), followSpeed * 1.15f);
                    if (FlatDistance(transform.position, FollowTarget()) <= followDistance + stopDistance)
                    {
                        state = CompanionState.Follow;
                    }
                    break;
            }

            ApplyIdleMotion();
        }

        public void WaitWithPlayer(float seconds = 0f)
        {
            state = CompanionState.Wait;
            stateTimer = seconds > 0f ? seconds : float.PositiveInfinity;
        }

        public void Recall()
        {
            state = CompanionState.Return;
            stateTimer = 0f;
        }

        public void Investigate(Vector3 worldPosition, float seconds = 3f)
        {
            investigationTarget = worldPosition;
            investigationTarget.y = transform.position.y;
            state = CompanionState.Investigate;
            stateTimer = Mathf.Max(0.5f, seconds);
        }

        public void CelebrateReview()
        {
            celebrationTimer = 0.65f;
        }

        private void CheckForNearbyInterest()
        {
            if (!inspectNearbyPoints || Time.time < nextInterestCheck) return;
            nextInterestCheck = Time.time + interestCooldown;

            RoscoInterestPoint closest = null;
            float closestDistance = interestSearchRadius;
            foreach (RoscoInterestPoint point in interestPoints)
            {
                if (point == null || !point.isActiveAndEnabled) continue;
                if (!point.Repeatable && visitedPoints.Contains(point)) continue;

                float distance = FlatDistance(transform.position, point.transform.position);
                if (distance <= closestDistance)
                {
                    closest = point;
                    closestDistance = distance;
                }
            }

            if (closest == null) return;
            if (!closest.Repeatable) visitedPoints.Add(closest);
            InterestDiscovered?.Invoke(closest.PointName);
            Investigate(closest.transform.position, closest.PauseSeconds);
        }

        private Vector3 FollowTarget()
        {
            Vector3 target = player.position - player.forward * followDistance;
            target.y = transform.position.y;
            return target;
        }

        private void MoveToward(Vector3 target, float speed)
        {
            Vector3 delta = target - transform.position;
            delta.y = 0f;
            if (delta.sqrMagnitude <= stopDistance * stopDistance)
            {
                Face(player.position);
                return;
            }

            transform.position += delta.normalized * speed * Time.deltaTime;
            Face(transform.position + delta);
        }

        private void Face(Vector3 point)
        {
            Vector3 direction = point - transform.position;
            direction.y = 0f;
            if (direction.sqrMagnitude <= 0.001f) return;
            transform.forward = Vector3.Slerp(transform.forward, direction.normalized, turnSpeed * Time.deltaTime);
        }

        private void ApplyIdleMotion()
        {
            float bob = Mathf.Sin(Time.time * idleBobSpeed) * idleBobHeight;
            float celebration = celebrationTimer > 0f ? Mathf.Sin((0.65f - celebrationTimer) * 18f) * 0.08f : 0f;
            celebrationTimer = Mathf.Max(0f, celebrationTimer - Time.deltaTime);
            transform.localScale = baseScale * (1f + celebration);
            Vector3 position = transform.position;
            position.y = groundY + bob;
            transform.position = position;
        }

        private static float FlatDistance(Vector3 first, Vector3 second)
        {
            first.y = 0f;
            second.y = 0f;
            return Vector3.Distance(first, second);
        }
    }
}
