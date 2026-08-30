using UnityEngine;

namespace GreenMachine.Park
{
    public sealed class XIVSessionSummary : MonoBehaviour
    {
        [SerializeField] private TextMesh display;
        [SerializeField] private XIVWalkSession session;

        private void Start()
        {
            if (session == null) session = FindFirstObjectByType<XIVWalkSession>();
            if (session != null) session.WalkCompleted += OnWalkCompleted;
            SetText(session == null
                ? "ARCHIVE GARDEN\nWALK SAVES HERE"
                : $"ARCHIVE GARDEN\nWALK SAVES HERE\nTOTAL WALKS {session.CompletedWalkCount}");
        }

        private void OnWalkCompleted(string destinationName)
        {
            WalkSessionRecord record = session.CurrentRecord;
            string destination = string.IsNullOrWhiteSpace(destinationName) ? "DESTINATION" : destinationName.ToUpperInvariant();
            SetText(
                $"{destination}\nWALK SAVED\n" +
                $"{record.distanceMeters:0.0} M  /  {record.pointsDiscovered} DISCOVERIES\n" +
                $"TOTAL WALKS {session.CompletedWalkCount}");
        }

        private void SetText(string value)
        {
            if (display != null) display.text = value;
        }

        private void OnDestroy()
        {
            if (session != null) session.WalkCompleted -= OnWalkCompleted;
        }
    }
}
