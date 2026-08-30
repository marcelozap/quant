using System;
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
            SetText(BuildOpeningText());
        }

        private void OnWalkCompleted(string destinationName)
        {
            WalkSessionRecord record = session.CurrentRecord;
            string destination = string.IsNullOrWhiteSpace(destinationName) ? "DESTINATION" : destinationName.ToUpperInvariant();
            SetText(
                $"{destination}\nWALK SAVED\n" +
                $"{record.distanceMeters:0.0} M  /  {record.pointsDiscovered} DISCOVERIES\n" +
                $"{record.interactions} MOMENTS\n" +
                $"TOTAL WALKS {session.CompletedWalkCount}");
        }

        private void SetText(string value)
        {
            if (display != null) display.text = value;
        }

        private string BuildOpeningText()
        {
            if (session == null) return "ARCHIVE GARDEN\nWALK SAVES HERE";

            WalkSessionRecord lastWalk = session.LastCompletedWalk;
            if (lastWalk == null)
            {
                return "ARCHIVE GARDEN\nWALK SAVES HERE\nTOTAL WALKS 0";
            }

            string destination = string.IsNullOrWhiteSpace(lastWalk.destinationName)
                ? "LAST WALK"
                : lastWalk.destinationName.ToUpperInvariant();
            return
                $"WELCOME BACK\n{destination}\n" +
                $"{FormatTimestamp(lastWalk.completedAtUtc)}\n" +
                $"TOTAL WALKS {session.CompletedWalkCount}";
        }

        private static string FormatTimestamp(string timestamp)
        {
            if (!DateTime.TryParse(timestamp, out DateTime parsed)) return "LOCAL MEMORY";
            return parsed.ToLocalTime().ToString("MMM d, h:mm tt");
        }

        private void OnDestroy()
        {
            if (session != null) session.WalkCompleted -= OnWalkCompleted;
        }
    }
}
