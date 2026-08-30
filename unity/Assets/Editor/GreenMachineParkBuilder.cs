using GreenMachine.Park;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace GreenMachine.Editor
{
    public static class GreenMachineParkBuilder
    {
        private static readonly (string name, Vector3 position, Color color)[] Districts =
        {
            ("Green Gate", new Vector3(0f, 0f, 0f), new Color(0.88f, 0.96f, 0.34f)),
            ("Semiconductor Speedway", new Vector3(22f, 0f, 12f), new Color(0.31f, 0.78f, 1f)),
            ("Macro Mountain", new Vector3(-25f, 0f, 20f), new Color(0.37f, 0.89f, 0.68f)),
            ("Earnings Arcade", new Vector3(30f, 0f, -17f), new Color(1f, 0.4f, 0.48f)),
            ("Tape Tunnel", new Vector3(-22f, 0f, -20f), new Color(0.65f, 0.39f, 1f)),
            ("Signal Square", new Vector3(3f, 0f, 31f), new Color(1f, 0.71f, 0.24f)),
            ("Account Observatory", new Vector3(-37f, 0f, -2f), new Color(0.42f, 0.6f, 0.96f)),
            ("Archive Garden", new Vector3(16f, 0f, -34f), new Color(0.96f, 0.56f, 0.76f)),
        };

        [MenuItem("XIV/Create First Playable World")]
        public static void CreatePark()
        {
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);
            GameObject ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ground.name = "Park Grounds";
            ground.transform.localScale = new Vector3(11f, 1f, 11f);
            ground.GetComponent<Renderer>().sharedMaterial = MaterialFor(new Color(0.12f, 0.28f, 0.24f));

            foreach (var district in Districts) CreateDistrict(district.name, district.position, district.color);
            CreatePlayer();
            CreateRosco();
            CreateWorldController();
            CreateFastTravel();
            EditorSceneManager.SaveScene(scene, "Assets/Scenes/XIVWorld.unity");
            Selection.activeGameObject = GameObject.Find("Marcelo");
        }

        private static void CreateDistrict(string districtName, Vector3 position, Color color)
        {
            GameObject root = new GameObject(districtName);
            root.transform.position = position;
            GameObject building = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            building.name = $"{districtName} Landmark";
            building.transform.SetParent(root.transform);
            building.transform.localScale = new Vector3(7f, 4f, 7f);
            building.transform.localPosition = new Vector3(0f, 2f, 0f);
            building.GetComponent<Renderer>().sharedMaterial = MaterialFor(color);

            GameObject beacon = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            beacon.name = "Event Beacon";
            beacon.transform.SetParent(root.transform);
            beacon.transform.localScale = Vector3.one * 1.3f;
            beacon.transform.localPosition = new Vector3(0f, 6.5f, 0f);
            beacon.GetComponent<Renderer>().sharedMaterial = MaterialFor(Color.Lerp(color, Color.white, 0.5f));

            GameObject label = new GameObject("District Label");
            label.transform.SetParent(root.transform);
            label.transform.localPosition = new Vector3(0f, 8f, 0f);
            TextMesh text = label.AddComponent<TextMesh>();
            text.text = districtName;
            text.anchor = TextAnchor.MiddleCenter;
            text.characterSize = 0.45f;
            text.fontSize = 48;
            text.color = Color.white;
        }

        private static void CreatePlayer()
        {
            GameObject player = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            player.name = "Marcelo";
            player.tag = "Player";
            player.transform.position = new Vector3(0f, 1f, -6f);
            Object.DestroyImmediate(player.GetComponent<Collider>());
            player.AddComponent<CharacterController>();
            Camera camera = Camera.main;
            camera.transform.position = player.transform.position + new Vector3(0f, 5f, -8f);
            camera.transform.LookAt(player.transform.position + Vector3.up * 1.4f);
            ThirdPersonCamera followCamera = camera.gameObject.AddComponent<ThirdPersonCamera>();
            SerializedObject cameraSerialized = new SerializedObject(followCamera);
            cameraSerialized.FindProperty("target").objectReferenceValue = player.transform;
            cameraSerialized.ApplyModifiedPropertiesWithoutUndo();
            ThirdPersonMover mover = player.AddComponent<ThirdPersonMover>();
            SerializedObject serialized = new SerializedObject(mover);
            serialized.FindProperty("cameraTransform").objectReferenceValue = camera.transform;
            serialized.ApplyModifiedPropertiesWithoutUndo();
        }

        private static void CreateRosco()
        {
            GameObject rosco = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            rosco.name = "Rosco";
            rosco.transform.position = new Vector3(-2f, 0.6f, -8f);
            rosco.transform.localScale = new Vector3(1.1f, 0.8f, 1.6f);
            rosco.GetComponent<Renderer>().sharedMaterial = MaterialFor(new Color(0.56f, 0.27f, 0.12f));
            RoscoCompanion companion = rosco.AddComponent<RoscoCompanion>();
            SerializedObject serialized = new SerializedObject(companion);
            serialized.FindProperty("player").objectReferenceValue = GameObject.Find("Marcelo").transform;
            serialized.ApplyModifiedPropertiesWithoutUndo();
        }

        private static void CreateWorldController()
        {
            GameObject world = new GameObject("Park World Controller");
            ParkWorldController controller = world.AddComponent<ParkWorldController>();
            SerializedObject serialized = new SerializedObject(controller);
            serialized.FindProperty("sun").objectReferenceValue = Object.FindFirstObjectByType<Light>();
            serialized.ApplyModifiedPropertiesWithoutUndo();
        }

        private static void CreateFastTravel()
        {
            GameObject travel = new GameObject("Park Fast Travel");
            ParkFastTravel fastTravel = travel.AddComponent<ParkFastTravel>();
            SerializedObject serialized = new SerializedObject(fastTravel);
            serialized.FindProperty("player").objectReferenceValue = GameObject.Find("Marcelo").transform;
            SerializedProperty destinations = serialized.FindProperty("destinations");
            destinations.arraySize = Districts.Length;
            for (int i = 0; i < Districts.Length; i++)
            {
                GameObject point = new GameObject($"{Districts[i].name} Arrival");
                point.transform.position = Districts[i].position + new Vector3(0f, 0.2f, -5f);
                SerializedProperty item = destinations.GetArrayElementAtIndex(i);
                item.FindPropertyRelative("districtName").stringValue = Districts[i].name;
                item.FindPropertyRelative("arrivalPoint").objectReferenceValue = point.transform;
            }
            serialized.ApplyModifiedPropertiesWithoutUndo();
        }

        private static Material MaterialFor(Color color)
        {
            Material material = new Material(Shader.Find("Universal Render Pipeline/Lit"));
            material.color = color;
            material.SetColor("_BaseColor", color);
            return material;
        }
    }
}
