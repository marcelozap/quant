using UnityEngine;

namespace GreenMachine.Park
{
    public sealed class XIVWalkGuide : MonoBehaviour
    {
        [SerializeField] private TextMesh display;
        [SerializeField] private XIVWalkSession session;
        [SerializeField] private RoscoCompanion rosco;
        [SerializeField] private Transform player;
        [SerializeField] private Transform destination;
        [SerializeField] [Min(0.5f)] private float messageDuration = 4f;

        private float messageTimer;
        private bool completed;

        public bool IsConfigured => display != null && session != null && rosco != null && player != null && destination != null;

        private void Start()
        {
            if (session == null) session = FindFirstObjectByType<XIVWalkSession>();
            if (rosco == null) rosco = FindFirstObjectByType<RoscoCompanion>();
            if (player == null) player = GameObject.Find("Marcelo")?.transform;
            if (destination == null) destination = GameObject.Find("Archive Garden")?.transform;
            if (session != null) session.WalkCompleted += OnWalkCompleted;
            if (rosco != null) rosco.InterestDiscovered += OnInterestDiscovered;
            SetDefaultText();
        }

        private void Update()
        {
            if (completed || display == null) return;
            if (messageTimer > 0f)
            {
                messageTimer -= Time.deltaTime;
                if (messageTimer > 0f) return;
            }

            SetDefaultText();
        }

        private void OnWalkCompleted(string destinationName)
        {
            completed = true;
            messageTimer = 0f;
            SetText($"WALK COMPLETE\n{destinationName}");
        }

        private void OnInterestDiscovered(string pointName)
        {
            messageTimer = messageDuration;
            SetText($"ROSCO NOTICED\n{pointName}\n\nKEEP GOING");
        }

        private void SetDefaultText()
        {
            if (rosco != null)
            {
                if (rosco.IsWaiting)
                {
                    SetText("ROSCO IS WAITING");
                    return;
                }

                if (rosco.IsInvestigating)
                {
                    SetText("ROSCO IS LOOKING\nAROUND");
                    return;
                }
            }

            if (player != null && destination != null)
            {
                float distance = FlatDistance(player.position, destination.position);
                SetText($"ARCHIVE GARDEN\n{distance:0} M");
                return;
            }

            SetText("ARCHIVE GARDEN ->\nWALK WITH ROSCO");
        }

        private void SetText(string value)
        {
            if (display != null) display.text = value;
        }

        private void OnDestroy()
        {
            if (session != null) session.WalkCompleted -= OnWalkCompleted;
            if (rosco != null) rosco.InterestDiscovered -= OnInterestDiscovered;
        }

        private static float FlatDistance(Vector3 first, Vector3 second)
        {
            first.y = 0f;
            second.y = 0f;
            return Vector3.Distance(first, second);
        }
    }
}
