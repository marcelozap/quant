using System.IO;
using GreenMachine.Data;
using GreenMachine.Park;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace GreenMachine.Editor
{
    public static class XIVWorldValidator
    {
        private const string ScenePath = "Assets/Scenes/XIVWorld.unity";

        [MenuItem("XIV/Validate First Playable World")]
        public static void ValidateFirstWorld()
        {
            if (!File.Exists(ScenePath))
            {
                Debug.LogError($"XIV validation failed: {ScenePath} does not exist. Run XIV/Create First Playable World first.");
                return;
            }

            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
            Scene scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            int passed = 0;
            int failed = 0;

            Check(scene.IsValid(), "XIVWorld scene is valid", ref passed, ref failed);
            Check(GameObject.Find("Marcelo")?.GetComponent<CharacterController>() != null, "Marcelo has a CharacterController", ref passed, ref failed);
            Check(GameObject.Find("Marcelo")?.GetComponent<ThirdPersonMover>() != null, "Marcelo has ThirdPersonMover", ref passed, ref failed);
            Check(GameObject.Find("Rosco")?.GetComponent<RoscoCompanion>() != null, "Rosco has RoscoCompanion", ref passed, ref failed);
            Check(GameObject.Find("Green Gate") != null, "Green Gate exists", ref passed, ref failed);
            Check(GameObject.Find("Archive Garden")?.GetComponent<XIVWalkDestination>() != null, "Archive Garden completes the walk", ref passed, ref failed);
            Check(GameObject.Find("Green Gate to Archive Garden Route") != null, "First walking route exists", ref passed, ref failed);
            Check(GameObject.Find("XIV Audio Atmosphere")?.GetComponent<XIVAudioAtmosphere>() != null, "Audio atmosphere exists", ref passed, ref failed);
            Check(GameObject.Find("XIV Audio Atmosphere")?.GetComponent<AudioSource>() != null, "Audio source exists", ref passed, ref failed);
            Check(GameObject.Find("XIV Walk Session")?.GetComponent<XIVWalkSession>() != null, "Walk session exists", ref passed, ref failed);
            Check(GameObject.Find("Green Machine Read Only Board")?.GetComponent<GreenMachineBoard>() != null, "Green Machine board is read-only", ref passed, ref failed);
            Check(GameObject.Find("XIV Systems Board")?.GetComponent<XIVSystemsBoard>() != null, "XIV Systems board exists", ref passed, ref failed);

            string sceneText = File.ReadAllText(ScenePath);
            Check(!sceneText.Contains("apiToken:"), "No serialized API token field exists", ref passed, ref failed);
            Check(!sceneText.Contains("GREEN_MACHINE_API_TOKEN"), "No environment token is serialized", ref passed, ref failed);

            if (failed == 0) Debug.Log($"XIV validation passed: {passed} checks in {ScenePath}.");
            else Debug.LogError($"XIV validation failed: {failed} checks failed and {passed} passed in {ScenePath}.");
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
