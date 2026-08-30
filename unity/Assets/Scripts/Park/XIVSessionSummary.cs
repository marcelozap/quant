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
            SetText("ARCHIVE GARDEN\nWALK SAVES HERE");
        }

        private void OnWalkCompleted(string destinationName)
        {
            WalkSessionRecord record = session.CurrentRecord;
            string destination = string.IsNullOrWhiteSpace(destinationName) ? "DESTINATION" : destinationName.ToUpperInvariant();
            SetText(
                $"{destination}\nWALK SAVED\n" +
                $"{record.distanceMeters:0.0} M  /  {record.pointsDiscovered} DISCOVERIES");
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
