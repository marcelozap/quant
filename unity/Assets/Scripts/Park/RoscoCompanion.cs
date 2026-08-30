using System.Collections.Generic;
using UnityEngine;
using UnityEngine.AI;
using UnityEngine.InputSystem;

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
        [SerializeField] private float catchUpDistance = 7f;
        [SerializeField] private float relocateDistance = 24f;
        [SerializeField] private float turnSpeed = 8f;
        [SerializeField] private float stopDistance = 0.35f;
        [SerializeField] private float greetingDuration = 1.4f;
        [SerializeField] private float investigationRadius = 0.4f;
        [SerializeField] private float idleBobHeight = 0.035f;
        [SerializeField] private float idleBobSpeed = 2.4f;
        [SerializeField] private bool inspectNearbyPoints = true;
        [SerializeField] private float interestSearchRadius = 10f;
        [SerializeField] private float interestCooldown = 7f;
        [SerializeField] private Animator animator;
        [SerializeField] private NavMeshAgent navigationAgent;

        private CompanionState state = CompanionState.Greeting;
        private Vector3 investigationTarget;
        private Vector3 baseScale;
        private Vector3 previousPosition;
        private float stateTimer;
        private float celebrationTimer;
        private float groundY;
        private float nextInterestCheck;
        private float currentSpeed;
        private RoscoInterestPoint[] interestPoints = System.Array.Empty<RoscoInterestPoint>();
        private readonly HashSet<RoscoInterestPoint> visitedPoints = new HashSet<RoscoInterestPoint>();

        private bool hasSpeedParameter;
        private bool hasStateParameter;
        private bool hasInvestigatingParameter;
        private bool hasCelebrateParameter;

        public event System.Action<string> InterestDiscovered;
        public string CurrentState => state.ToString();
        public float CurrentSpeed => currentSpeed;
        public bool IsInvestigating => state == CompanionState.Investigate;
        public bool IsWaiting => state == CompanionState.Wait;
        public bool IsCelebrating => celebrationTimer > 0f;

        private void Awake()
        {
            baseScale = transform.localScale;
            stateTimer = greetingDuration;
            groundY = transform.position.y;
            previousPosition = transform.position;
        }

        private void Start()
        {
            if (animator == null) animator = GetComponentInChildren<Animator>();
            if (navigationAgent == null) navigationAgent = GetComponent<NavMeshAgent>();
            if (navigationAgent != null)
            {
                navigationAgent.updatePosition = false;
                navigationAgent.updateRotation = false;
                navigationAgent.stoppingDistance = stopDistance;
            }
            CacheAnimatorParameters();
            interestPoints = FindObjectsByType<RoscoInterestPoint>(FindObjectsSortMode.None);
        }

        private void Update()
        {
            if (player == null) return;

            ReadCompanionInput();

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
                    MoveWithDistanceBand();
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

            currentSpeed = FlatDistance(transform.position, previousPosition) / Mathf.Max(Time.deltaTime, 0.001f);
            previousPosition = transform.position;
            ApplyIdleMotion();
            UpdateAnimator();
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

        public void RejoinPlayer()
        {
            if (player == null) return;
            transform.position = FollowTarget();
            transform.forward = player.forward;
            groundY = transform.position.y;
            previousPosition = transform.position;
            if (navigationAgent != null && navigationAgent.isOnNavMesh) navigationAgent.Warp(transform.position);
            state = CompanionState.Follow;
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

        private void ReadCompanionInput()
        {
            if (Keyboard.current == null) return;
            if (Keyboard.current.rKey.wasPressedThisFrame)
            {
                Recall();
                return;
            }

            if (Keyboard.current.fKey.wasPressedThisFrame)
            {
                if (state == CompanionState.Wait) Recall();
                else WaitWithPlayer();
            }
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
            closest.MarkDiscovered();
            InterestDiscovered?.Invoke(closest.PointName);
            Investigate(closest.transform.position, closest.PauseSeconds);
        }

        private Vector3 FollowTarget()
        {
            Vector3 target = player.position - player.forward * followDistance;
            target.y = transform.position.y;
            return target;
        }

        private void MoveWithDistanceBand()
        {
            Vector3 target = FollowTarget();
            float distance = FlatDistance(transform.position, target);
            if (distance >= relocateDistance)
            {
                RejoinPlayer();
                return;
            }

            float catchUp = Mathf.InverseLerp(catchUpDistance, relocateDistance, distance);
            float speed = followSpeed * Mathf.Lerp(1f, 2.2f, catchUp);
            MoveToward(target, speed);
        }

        private void MoveToward(Vector3 target, float speed)
        {
            Vector3 travelTarget = target;
            if (navigationAgent != null && navigationAgent.isOnNavMesh)
            {
                navigationAgent.speed = speed;
                navigationAgent.SetDestination(target);
                if (navigationAgent.steeringTarget != Vector3.zero) travelTarget = navigationAgent.steeringTarget;
                navigationAgent.nextPosition = transform.position;
            }

            Vector3 delta = travelTarget - transform.position;
            delta.y = 0f;
            if (delta.sqrMagnitude <= stopDistance * stopDistance)
            {
                Face(state == CompanionState.Investigate ? investigationTarget : player.position);
                return;
            }

            transform.position += delta.normalized * speed * Time.deltaTime;
            if (navigationAgent != null && navigationAgent.isOnNavMesh) navigationAgent.nextPosition = transform.position;
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

        private void CacheAnimatorParameters()
        {
            if (animator == null) return;
            hasSpeedParameter = HasAnimatorParameter("Speed", AnimatorControllerParameterType.Float);
            hasStateParameter = HasAnimatorParameter("State", AnimatorControllerParameterType.Int);
            hasInvestigatingParameter = HasAnimatorParameter("IsInvestigating", AnimatorControllerParameterType.Bool);
            hasCelebrateParameter = HasAnimatorParameter("Celebrate", AnimatorControllerParameterType.Bool);
        }

        private void UpdateAnimator()
        {
            if (animator == null) return;
            if (hasSpeedParameter) animator.SetFloat("Speed", currentSpeed);
            if (hasStateParameter) animator.SetInteger("State", (int)state);
            if (hasInvestigatingParameter) animator.SetBool("IsInvestigating", state == CompanionState.Investigate);
            if (hasCelebrateParameter) animator.SetBool("Celebrate", celebrationTimer > 0f);
        }

        private bool HasAnimatorParameter(string parameterName, AnimatorControllerParameterType parameterType)
        {
            foreach (AnimatorControllerParameter parameter in animator.parameters)
            {
                if (parameter.name == parameterName && parameter.type == parameterType) return true;
            }
            return false;
        }

        private static float FlatDistance(Vector3 first, Vector3 second)
        {
            first.y = 0f;
            second.y = 0f;
            return Vector3.Distance(first, second);
        }
    }
}
