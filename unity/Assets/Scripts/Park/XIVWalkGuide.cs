using UnityEngine;

namespace GreenMachine.Park
{
    public sealed class XIVWalkGuide : MonoBehaviour
    {
        [SerializeField] private TextMesh display;
        [SerializeField] private XIVWalkSession session;
        [SerializeField] private RoscoCompanion rosco;

        private void Start()
        {
            if (session == null) session = FindFirstObjectByType<XIVWalkSession>();
            if (rosco == null) rosco = FindFirstObjectByType<RoscoCompanion>();
            if (session != null) session.WalkCompleted += OnWalkCompleted;
            if (rosco != null) rosco.InterestDiscovered += OnInterestDiscovered;
            SetText("ARCHIVE GARDEN ->\nWALK WITH ROSCO");
        }

        private void OnWalkCompleted(string destinationName)
        {
            SetText($"WALK COMPLETE\n{destinationName}");
        }

        private void OnInterestDiscovered(string pointName)
        {
            SetText($"ROSCO NOTICED\n{pointName}\n\nKEEP GOING");
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
    }
}
