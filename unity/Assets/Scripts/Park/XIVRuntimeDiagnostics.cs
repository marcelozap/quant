using System;
using System.IO;
using UnityEngine;
using UnityEngine.AI;

namespace GreenMachine.Park
{
    public sealed class XIVRuntimeDiagnostics : MonoBehaviour
    {
        public bool IsReady { get; private set; }
        public string LastReport { get; private set; } = string.Empty;

        private void Start()
        {
            StartCoroutine(ReportReadinessAfterStartup());
        }

        private System.Collections.IEnumerator ReportReadinessAfterStartup()
        {
            yield return new WaitForSecondsRealtime(0.25f);
            ReportReadiness();
        }

        private void ReportReadiness()
        {
            Camera camera = Camera.main;
            GameObject player = GameObject.Find("Marcelo");
            GameObject rosco = GameObject.Find("Rosco");
            GameObject route = GameObject.Find("Green Gate to Archive Garden Route");
            GameObject destination = GameObject.Find("Archive Garden");
            bool navMeshReady = player != null && NavMesh.SamplePosition(player.transform.position, out _, 2f, NavMesh.AllAreas);
            bool saveBoundaryReady = CanUseSaveDirectory();

            IsReady = camera != null && player != null && rosco != null && navMeshReady &&
                route != null && destination != null && saveBoundaryReady;
            LastReport =
                $"camera={Flag(camera != null)} player={Flag(player != null)} rosco={Flag(rosco != null)} " +
                $"navmesh={Flag(navMeshReady)} route={Flag(route != null)} destination={Flag(destination != null)} " +
                $"save_root={Flag(saveBoundaryReady)}";

            if (IsReady) Debug.Log($"XIV runtime ready: {LastReport}");
            else Debug.LogError($"XIV runtime incomplete: {LastReport}");
        }

        private static string Flag(bool value) => value ? "true" : "false";

        private static bool CanUseSaveDirectory()
        {
            try
            {
                string path = Path.Combine(Application.persistentDataPath, "XIV");
                Directory.CreateDirectory(path);
                return Directory.Exists(path);
            }
            catch (IOException)
            {
                return false;
            }
            catch (UnauthorizedAccessException)
            {
                return false;
            }
            catch (ArgumentException)
            {
                return false;
            }
        }
    }
}
