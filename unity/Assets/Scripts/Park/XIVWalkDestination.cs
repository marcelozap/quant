using UnityEngine;

namespace GreenMachine.Park
{
    [RequireComponent(typeof(SphereCollider))]
    public sealed class XIVWalkDestination : MonoBehaviour
    {
        [SerializeField] private string destinationName = "Archive Garden";

        private XIVWalkSession session;
        private RoscoCompanion rosco;
        private bool completed;

        private void Start()
        {
            session = FindFirstObjectByType<XIVWalkSession>();
            rosco = FindFirstObjectByType<RoscoCompanion>();
            SphereCollider trigger = GetComponent<SphereCollider>();
            trigger.isTrigger = true;
            trigger.radius = 5f;
            trigger.center = Vector3.up * 1.5f;
        }

        private void OnTriggerEnter(Collider other)
        {
            if (completed || !other.CompareTag("Player") || session == null) return;

            completed = true;
            session.CompleteWalk(destinationName);
            if (rosco != null) rosco.CelebrateReview();
        }
    }
}
