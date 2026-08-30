using System.IO;
using GreenMachine.Data;
using GreenMachine.Park;
using Unity.AI.Navigation;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.AI;
using UnityEngine.SceneManagement;

namespace GreenMachine.Editor
{
    public static class XIVWorldValidator
    {
        private const string ScenePath = "Assets/Scenes/XIVWorld.unity";
        private static readonly string[] RequiredLandmarks =
        {
            "Green Gate",
            "Semiconductor Speedway",
            "Macro Mountain",
            "Earnings Arcade",
            "Tape Tunnel",
            "Signal Square",
            "Account Observatory",
            "Archive Garden",
        };

        [MenuItem("XIV/Validate First Playable World")]
        public static void ValidateFirstWorld()
        {
            ValidateFirstWorldScene();
        }

        public static void BuildAndValidateFirstWorldBatch()
        {
            GreenMachineParkBuilder.CreatePark();
            bool valid = ValidateFirstWorldScene();
            EditorApplication.Exit(valid ? 0 : 1);
        }

        public static bool ValidateFirstWorldScene()
        {
            if (!File.Exists(ScenePath))
            {
                Debug.LogError($"XIV validation failed: {ScenePath} does not exist. Run XIV/Create First Playable World first.");
                return false;
            }

            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return false;
            Scene scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            int passed = 0;
            int failed = 0;

            Check(scene.IsValid(), "XIVWorld scene is valid", ref passed, ref failed);
            NavMeshSurface navigationSurface = GameObject.Find("Park Grounds")?.GetComponent<NavMeshSurface>();
            Check(navigationSurface != null, "Park grounds have a NavMesh surface", ref passed, ref failed);
            Check(navigationSurface != null && navigationSurface.navMeshData != null, "Park grounds have a baked NavMesh", ref passed, ref failed);
            Check(GameObject.Find("Marcelo")?.GetComponent<CharacterController>() != null, "Marcelo has a CharacterController", ref passed, ref failed);
            Check(GameObject.Find("Marcelo")?.GetComponent<ThirdPersonMover>() != null, "Marcelo has ThirdPersonMover", ref passed, ref failed);
            Check(GameObject.Find("Main Camera")?.GetComponent<ThirdPersonCamera>() != null, "Main Camera has ThirdPersonCamera", ref passed, ref failed);
            Check(GameObject.Find("Main Camera")?.GetComponent<ThirdPersonCamera>()?.FramesSecondaryTarget == true, "Camera frames Marcelo and Rosco", ref passed, ref failed);
            Check(GameObject.Find("Rosco")?.GetComponent<RoscoCompanion>() != null, "Rosco has RoscoCompanion", ref passed, ref failed);
            Check(GameObject.Find("Rosco")?.GetComponent<RoscoProceduralAnimator>() != null, "Rosco has expressive procedural animation", ref passed, ref failed);
            Check(GameObject.Find("Rosco")?.GetComponent<NavMeshAgent>() != null, "Rosco has a navigation agent", ref passed, ref failed);
            foreach (string landmark in RequiredLandmarks)
            {
                Check(GameObject.Find(landmark) != null, $"Landmark exists: {landmark}", ref passed, ref failed);
            }
            GameObject greenGate = GameObject.Find("Green Gate");
            Check(greenGate != null, "Green Gate exists", ref passed, ref failed);
            Check(GameObject.Find("XIV Gate Sign")?.GetComponent<XIVBillboard>() != null, "Green Gate sign faces the camera", ref passed, ref failed);
            GameObject archiveGarden = GameObject.Find("Archive Garden");
            Check(archiveGarden?.GetComponent<XIVWalkDestination>() != null, "Archive Garden completes the walk", ref passed, ref failed);
            SphereCollider destinationTrigger = archiveGarden?.GetComponent<SphereCollider>();
            Check(destinationTrigger != null && destinationTrigger.isTrigger, "Archive Garden has a trigger destination", ref passed, ref failed);
            Check(GameObject.Find("XIV Session Summary")?.GetComponent<XIVSessionSummary>() != null, "Archive Garden has a session summary", ref passed, ref failed);
            Check(greenGate != null && archiveGarden != null && archiveGarden.transform.position.z > greenGate.transform.position.z,
                "Archive Garden sits beyond Green Gate", ref passed, ref failed);
            Check(GameObject.Find("Green Gate to Archive Garden Route") != null, "First walking route exists", ref passed, ref failed);
            GameObject route = GameObject.Find("Green Gate to Archive Garden Route");
            int routeDiscoveries = route == null ? 0 : route.GetComponentsInChildren<RoscoInterestPoint>(true).Length;
            Check(routeDiscoveries >= 3, "First route has at least three Rosco discoveries", ref passed, ref failed);
            int routeMotionProps = route == null ? 0 : route.GetComponentsInChildren<XIVWindMotion>(true).Length;
            Check(routeMotionProps >= 3, "First route has audio-reactive motion props", ref passed, ref failed);
            Check(GameObject.Find("XIV Audio Atmosphere")?.GetComponent<XIVAudioAtmosphere>() != null, "Audio atmosphere exists", ref passed, ref failed);
            Check(GameObject.Find("XIV Audio Atmosphere")?.GetComponent<AudioSource>() != null, "Audio source exists", ref passed, ref failed);
            Check(GameObject.Find("XIV Walk Session")?.GetComponent<XIVWalkSession>() != null, "Walk session exists", ref passed, ref failed);
            Check(GameObject.Find("XIV Walk Guide")?.GetComponent<XIVWalkGuide>() != null, "First walk guide exists", ref passed, ref failed);
            Check(GameObject.Find("Park World Controller")?.GetComponent<ParkWorldController>() != null, "World controller exists", ref passed, ref failed);
            Check(GameObject.Find("Park Fast Travel")?.GetComponent<ParkFastTravel>() != null, "Fast travel registry exists", ref passed, ref failed);
            Check(GameObject.Find("Green Machine Read Only Board")?.GetComponent<GreenMachineBoard>() != null, "Green Machine board is read-only", ref passed, ref failed);
            Check(GameObject.Find("XIV Systems Board")?.GetComponent<XIVSystemsBoard>() != null, "XIV Systems board exists", ref passed, ref failed);

            string sceneText = File.ReadAllText(ScenePath);
            Check(!sceneText.Contains("apiToken:"), "No serialized API token field exists", ref passed, ref failed);
            Check(!sceneText.Contains("GREEN_MACHINE_API_TOKEN"), "No environment token is serialized", ref passed, ref failed);

            if (failed == 0) Debug.Log($"XIV validation passed: {passed} checks in {ScenePath}.");
            else Debug.LogError($"XIV validation failed: {failed} checks failed and {passed} passed in {ScenePath}.");
            return failed == 0;
        }

        private static void Check(bool condition, string message, ref int passed, ref int failed)
        {
            if (condition)
            {
                passed++;
                Debug.Log($"XIV validation: PASS - {message}");
            }
            else
            {
                failed++;
                Debug.LogError($"XIV validation: FAIL - {message}");
            }
        }
    }
}
