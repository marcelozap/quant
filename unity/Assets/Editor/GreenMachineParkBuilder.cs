using GreenMachine.Data;
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
            ("Archive Garden", new Vector3(16f, 0f, 34f), new Color(0.96f, 0.56f, 0.76f)),
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
            CreateWalkRoute();
            CreatePlayer();
            CreateRosco();
            CreateWorldController();
            CreateAudioAtmosphere();
            CreateWalkSession();
            CreateGreenMachineBoard();
            CreateXivSystemsBoard();
            CreateFastTravel();
            if (!AssetDatabase.IsValidFolder("Assets/Scenes")) AssetDatabase.CreateFolder("Assets", "Scenes");
            EditorSceneManager.SaveScene(scene, "Assets/Scenes/XIVWorld.unity");
            Selection.activeGameObject = GameObject.Find("Marcelo");
        }

        private static void CreateWalkRoute()
        {
            GameObject route = new GameObject("Green Gate to Archive Garden Route");
            Vector3[] waypoints =
            {
                new Vector3(0f, 0f, 5f),
                new Vector3(3f, 0f, 12f),
                new Vector3(10f, 0f, 22f),
                new Vector3(16f, 0f, 30f),
                new Vector3(16f, 0f, 34f),
            };

            for (int i = 0; i < waypoints.Length - 1; i++)
            {
                CreatePathSegment(route.transform, waypoints[i], waypoints[i + 1]);
            }

            CreateInterestPoint(route.transform, "Wind chime", new Vector3(3f, 0.3f, 12f), new Color(1f, 0.7f, 0.28f));
            CreateInterestPoint(route.transform, "Garden light", new Vector3(10f, 0.3f, 22f), new Color(0.36f, 0.86f, 0.72f));
            CreateInterestPoint(route.transform, "Archive marker", new Vector3(16f, 0.3f, 30f), new Color(0.95f, 0.56f, 0.76f));
            CreateRouteDressing(route.transform);
        }

        private static void CreateRouteDressing(Transform parent)
        {
            CreateTree(parent, "Route Tree A", new Vector3(-1.2f, 0f, 13.5f), 0.95f);
            CreateTree(parent, "Route Tree B", new Vector3(6.7f, 0f, 15f), 1.1f);
            CreateTree(parent, "Route Tree C", new Vector3(6.8f, 0f, 24.5f), 0.85f);
            CreateTree(parent, "Route Tree D", new Vector3(13.5f, 0f, 25f), 1.15f);

            CreateRouteLantern(parent, "Route Lantern A", new Vector3(1.1f, 0f, 9f));
            CreateRouteLantern(parent, "Route Lantern B", new Vector3(8.1f, 0f, 18f));
            CreateRouteLantern(parent, "Route Lantern C", new Vector3(14.3f, 0f, 27f));
        }

        private static void CreateTree(Transform parent, string name, Vector3 position, float scale)
        {
            GameObject tree = new GameObject(name);
            tree.transform.SetParent(parent);
            tree.transform.localPosition = position;
            tree.transform.localScale = Vector3.one * scale;
            CreatePart(PrimitiveType.Cylinder, "Tree Trunk", tree.transform, new Vector3(0f, 1.1f, 0f), new Vector3(0.32f, 1.1f, 0.32f), new Color(0.28f, 0.12f, 0.06f));
            CreatePart(PrimitiveType.Sphere, "Tree Canopy", tree.transform, new Vector3(0f, 2.7f, 0f), new Vector3(1.35f, 1.7f, 1.35f), new Color(0.12f, 0.42f, 0.27f));
        }

        private static void CreateRouteLantern(Transform parent, string name, Vector3 position)
        {
            GameObject lantern = new GameObject(name);
            lantern.transform.SetParent(parent);
            lantern.transform.localPosition = position;
            CreatePart(PrimitiveType.Cylinder, "Lantern Post", lantern.transform, new Vector3(0f, 1.2f, 0f), new Vector3(0.12f, 1.2f, 0.12f), new Color(0.08f, 0.1f, 0.13f));
            CreatePart(PrimitiveType.Sphere, "Lantern", lantern.transform, new Vector3(0f, 2.45f, 0f), new Vector3(0.3f, 0.42f, 0.3f), new Color(1f, 0.66f, 0.24f));
            CreatePointLight(lantern.transform, "Route Glow", new Vector3(0f, 2.45f, 0f), new Color(1f, 0.48f, 0.2f));
        }

        private static void CreatePathSegment(Transform parent, Vector3 start, Vector3 end)
        {
            Vector3 direction = end - start;
            direction.y = 0f;
            GameObject segment = GameObject.CreatePrimitive(PrimitiveType.Cube);
            segment.name = "Route Path";
            segment.transform.SetParent(parent);
            segment.transform.position = (start + end) * 0.5f + Vector3.up * 0.04f;
            segment.transform.localScale = new Vector3(3.2f, 0.08f, direction.magnitude);
            segment.transform.rotation = Quaternion.LookRotation(direction.normalized, Vector3.up);
            segment.GetComponent<Renderer>().sharedMaterial = MaterialFor(new Color(0.78f, 0.69f, 0.48f));
        }

        private static void CreateInterestPoint(Transform parent, string name, Vector3 position, Color color)
        {
            GameObject point = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            point.name = name;
            point.transform.SetParent(parent);
            point.transform.position = position;
            point.transform.localScale = Vector3.one * 0.55f;
            point.GetComponent<Renderer>().sharedMaterial = MaterialFor(color);
            RoscoInterestPoint interest = point.AddComponent<RoscoInterestPoint>();
            SerializedObject serialized = new SerializedObject(interest);
            serialized.FindProperty("pointName").stringValue = name;
            serialized.ApplyModifiedPropertiesWithoutUndo();
            CreatePointLight(point.transform, "Interest Glow", Vector3.up * 1.1f, color);
        }

        private static void CreateDistrict(string districtName, Vector3 position, Color color)
        {
            GameObject root = new GameObject(districtName);
            root.transform.position = position;
            if (districtName == "Green Gate")
            {
                CreateGreenGate(root.transform, color);
                return;
            }
            if (districtName == "Archive Garden")
            {
                CreateArchiveGarden(root.transform, color);
                return;
            }

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

        private static void CreateGreenGate(Transform parent, Color accentColor)
        {
            Color stone = new Color(0.07f, 0.24f, 0.25f);
            Color trim = new Color(0.93f, 0.77f, 0.35f);
            Color coral = new Color(0.92f, 0.35f, 0.34f);

            CreatePart(PrimitiveType.Cylinder, "Left Gate Tower", parent, new Vector3(-5f, 3.4f, 0f), new Vector3(2.8f, 3.4f, 2.8f), stone);
            CreatePart(PrimitiveType.Cylinder, "Right Gate Tower", parent, new Vector3(5f, 3.4f, 0f), new Vector3(2.8f, 3.4f, 2.8f), stone);
            CreatePart(PrimitiveType.Cube, "Gate Header", parent, new Vector3(0f, 6.2f, 0f), new Vector3(10.8f, 1.4f, 1.4f), stone);
            CreatePart(PrimitiveType.Cube, "Gold Header Trim", parent, new Vector3(0f, 7f, -0.04f), new Vector3(11.3f, 0.16f, 1.55f), trim);
            CreatePart(PrimitiveType.Cube, "Left Gate Door", parent, new Vector3(-2.1f, 2.2f, 0.18f), new Vector3(0.55f, 4.4f, 0.65f), coral);
            CreatePart(PrimitiveType.Cube, "Right Gate Door", parent, new Vector3(2.1f, 2.2f, 0.18f), new Vector3(0.55f, 4.4f, 0.65f), coral);

            foreach (float x in new[] { -5f, 5f })
            {
                string side = x < 0f ? "Left" : "Right";
                CreatePart(PrimitiveType.Cylinder, $"{side} Tower Crown Lower", parent, new Vector3(x, 7.18f, 0f), new Vector3(3.2f, 0.3f, 3.2f), trim);
                CreatePart(PrimitiveType.Cylinder, $"{side} Tower Crown Upper", parent, new Vector3(x, 7.8f, 0f), new Vector3(2.35f, 0.22f, 2.35f), accentColor);
                CreatePart(PrimitiveType.Cube, $"{side} Ticket Window", parent, new Vector3(x, 2.8f, -2.78f), new Vector3(1.05f, 0.68f, 0.1f), trim);
                CreatePart(PrimitiveType.Cube, $"{side} Ticket Awning", parent, new Vector3(x, 3.65f, -2.95f), new Vector3(1.35f, 0.1f, 0.42f), coral);
                CreatePlanter(parent, $"{side} Gate Planter", new Vector3(x * 1.55f, 0f, -2.2f), accentColor);
            }

            for (int i = -1; i <= 1; i++)
            {
                CreatePart(PrimitiveType.Cube, $"Left Gate Light {i + 2}", parent, new Vector3(-5f, 2.2f + i * 1.55f, -1.43f), new Vector3(0.48f, 0.7f, 0.12f), accentColor);
                CreatePart(PrimitiveType.Cube, $"Right Gate Light {i + 2}", parent, new Vector3(5f, 2.2f + i * 1.55f, -1.43f), new Vector3(0.48f, 0.7f, 0.12f), accentColor);
            }

            CreatePointLight(parent, "Left Gate Glow", new Vector3(-4.2f, 4.3f, -1.8f), accentColor);
            CreatePointLight(parent, "Right Gate Glow", new Vector3(4.2f, 4.3f, -1.8f), coral);

            GameObject sign = new GameObject("XIV Gate Sign");
            sign.transform.SetParent(parent);
            sign.transform.localPosition = new Vector3(0f, 6.35f, -0.78f);
            TextMesh signText = sign.AddComponent<TextMesh>();
            signText.text = "XIV";
            signText.anchor = TextAnchor.MiddleCenter;
            signText.alignment = TextAlignment.Center;
            signText.characterSize = 0.95f;
            signText.fontSize = 72;
            signText.fontStyle = FontStyle.Bold;
            signText.color = Color.white;
        }

        private static void CreatePlanter(Transform parent, string name, Vector3 position, Color flowerColor)
        {
            GameObject planter = new GameObject(name);
            planter.transform.SetParent(parent);
            planter.transform.localPosition = position;
            CreatePart(PrimitiveType.Cube, "Planter Box", planter.transform, new Vector3(0f, 0.45f, 0f), new Vector3(0.9f, 0.45f, 0.58f), new Color(0.65f, 0.3f, 0.12f));
            CreatePart(PrimitiveType.Sphere, "Planter Leaves", planter.transform, new Vector3(0f, 1.2f, 0f), new Vector3(0.78f, 0.56f, 0.58f), new Color(0.12f, 0.52f, 0.24f));
            CreatePart(PrimitiveType.Sphere, "Planter Flower", planter.transform, new Vector3(0.32f, 1.52f, -0.08f), new Vector3(0.18f, 0.18f, 0.18f), flowerColor);
        }

        private static void CreateArchiveGarden(Transform parent, Color accentColor)
        {
            Color ground = new Color(0.08f, 0.22f, 0.18f);
            Color stone = new Color(0.18f, 0.28f, 0.3f);
            Color flower = new Color(0.95f, 0.56f, 0.76f);
            Color memory = new Color(0.52f, 0.75f, 0.95f);

            CreatePart(PrimitiveType.Cylinder, "Archive Garden Plinth", parent, new Vector3(0f, 0.28f, 0f), new Vector3(5.2f, 0.28f, 5.2f), ground);
            CreatePart(PrimitiveType.Cylinder, "Archive Memory Marker", parent, new Vector3(0f, 1.25f, 0f), new Vector3(0.65f, 1.25f, 0.65f), memory);
            CreatePart(PrimitiveType.Sphere, "Archive Memory Glow", parent, new Vector3(0f, 3.1f, 0f), new Vector3(0.9f, 0.9f, 0.9f), accentColor);
            CreatePointLight(parent, "Archive Garden Glow", new Vector3(0f, 2.7f, 0f), accentColor);

            Vector3[] memoryStones =
            {
                new Vector3(-2.8f, 0.65f, -1.8f),
                new Vector3(-2.2f, 0.65f, 2.1f),
                new Vector3(2.1f, 0.65f, 2.2f),
                new Vector3(2.9f, 0.65f, -1.5f),
            };
            for (int i = 0; i < memoryStones.Length; i++)
            {
                CreatePart(PrimitiveType.Sphere, $"Memory Stone {i + 1}", parent, memoryStones[i], new Vector3(0.58f, 0.8f, 0.58f), stone);
            }

            CreateTree(parent, "Archive Tree A", new Vector3(-6.2f, 0f, -3.6f), 1.15f);
            CreateTree(parent, "Archive Tree B", new Vector3(-6.8f, 0f, 3.5f), 0.95f);
            CreateTree(parent, "Archive Tree C", new Vector3(6.4f, 0f, 3.2f), 1.1f);
            CreateTree(parent, "Archive Tree D", new Vector3(6.6f, 0f, -3.6f), 0.9f);
            CreatePointLight(parent, "Archive Flower Light", new Vector3(0f, 0.7f, -4.5f), flower);
            SphereCollider destinationTrigger = parent.gameObject.AddComponent<SphereCollider>();
            destinationTrigger.isTrigger = true;
            destinationTrigger.radius = 5f;
            destinationTrigger.center = Vector3.up * 1.5f;
            parent.gameObject.AddComponent<XIVWalkDestination>();

            GameObject sign = new GameObject("Archive Garden Sign");
            sign.transform.SetParent(parent);
            sign.transform.localPosition = new Vector3(0f, 4.2f, -0.55f);
            TextMesh signText = sign.AddComponent<TextMesh>();
            signText.text = "ARCHIVE GARDEN";
            signText.anchor = TextAnchor.MiddleCenter;
            signText.alignment = TextAlignment.Center;
            signText.characterSize = 0.36f;
            signText.fontSize = 48;
            signText.color = Color.white;
        }

        private static GameObject CreatePart(
            PrimitiveType type,
            string name,
            Transform parent,
            Vector3 localPosition,
            Vector3 localScale,
            Color color)
        {
            GameObject part = GameObject.CreatePrimitive(type);
            part.name = name;
            part.transform.SetParent(parent);
            part.transform.localPosition = localPosition;
            part.transform.localScale = localScale;
            part.GetComponent<Renderer>().sharedMaterial = MaterialFor(color);
            return part;
        }

        private static void CreatePointLight(Transform parent, string name, Vector3 localPosition, Color color)
        {
            GameObject lightObject = new GameObject(name);
            lightObject.transform.SetParent(parent);
            lightObject.transform.localPosition = localPosition;
            Light light = lightObject.AddComponent<Light>();
            light.type = LightType.Point;
            light.color = color;
            light.intensity = 3f;
            light.range = 12f;
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
            GameObject rosco = new GameObject("Rosco");
            rosco.transform.position = new Vector3(-2f, 0.18f, -8f);

            Color fur = new Color(0.56f, 0.27f, 0.12f);
            Color lightFur = new Color(0.82f, 0.58f, 0.34f);
            Color dark = new Color(0.025f, 0.018f, 0.015f);
            Color collar = new Color(0.92f, 0.25f, 0.28f);

            CreateRoscoPart(PrimitiveType.Sphere, "Rosco Body", rosco.transform, new Vector3(0f, 0.9f, 0f), new Vector3(1.25f, 0.78f, 1.55f), fur, Quaternion.identity);
            CreateRoscoPart(PrimitiveType.Sphere, "Rosco Head", rosco.transform, new Vector3(0f, 1.45f, 0.95f), new Vector3(0.92f, 0.86f, 0.9f), fur, Quaternion.identity);
            CreateRoscoPart(PrimitiveType.Sphere, "Rosco Muzzle", rosco.transform, new Vector3(0f, 1.25f, 1.62f), new Vector3(0.5f, 0.34f, 0.42f), lightFur, Quaternion.identity);
            CreateRoscoPart(PrimitiveType.Sphere, "Rosco Nose", rosco.transform, new Vector3(0f, 1.3f, 1.98f), new Vector3(0.18f, 0.14f, 0.14f), dark, Quaternion.identity);

            CreateRoscoPart(PrimitiveType.Capsule, "Rosco Ear Left", rosco.transform, new Vector3(-0.48f, 1.9f, 0.82f), new Vector3(0.28f, 0.62f, 0.24f), fur, Quaternion.Euler(0f, 0f, -18f));
            CreateRoscoPart(PrimitiveType.Capsule, "Rosco Ear Right", rosco.transform, new Vector3(0.48f, 1.9f, 0.82f), new Vector3(0.28f, 0.62f, 0.24f), fur, Quaternion.Euler(0f, 0f, 18f));
            CreateRoscoPart(PrimitiveType.Sphere, "Rosco Eye Left", rosco.transform, new Vector3(-0.31f, 1.62f, 1.68f), new Vector3(0.1f, 0.12f, 0.08f), dark, Quaternion.identity);
            CreateRoscoPart(PrimitiveType.Sphere, "Rosco Eye Right", rosco.transform, new Vector3(0.31f, 1.62f, 1.68f), new Vector3(0.1f, 0.12f, 0.08f), dark, Quaternion.identity);

            CreateRoscoPart(PrimitiveType.Capsule, "Rosco Front Leg Left", rosco.transform, new Vector3(-0.43f, 0.38f, 0.62f), new Vector3(0.25f, 0.55f, 0.25f), lightFur, Quaternion.identity);
            CreateRoscoPart(PrimitiveType.Capsule, "Rosco Front Leg Right", rosco.transform, new Vector3(0.43f, 0.38f, 0.62f), new Vector3(0.25f, 0.55f, 0.25f), lightFur, Quaternion.identity);
            CreateRoscoPart(PrimitiveType.Capsule, "Rosco Back Leg Left", rosco.transform, new Vector3(-0.43f, 0.38f, -0.58f), new Vector3(0.28f, 0.6f, 0.28f), fur, Quaternion.identity);
            CreateRoscoPart(PrimitiveType.Capsule, "Rosco Back Leg Right", rosco.transform, new Vector3(0.43f, 0.38f, -0.58f), new Vector3(0.28f, 0.6f, 0.28f), fur, Quaternion.identity);
            CreateRoscoPart(PrimitiveType.Capsule, "Rosco Tail", rosco.transform, new Vector3(0f, 1.08f, -1.25f), new Vector3(0.2f, 0.72f, 0.2f), lightFur, Quaternion.Euler(-35f, 0f, 0f));
            CreateRoscoPart(PrimitiveType.Cylinder, "Rosco Collar", rosco.transform, new Vector3(0f, 1.62f, 0.92f), new Vector3(0.52f, 0.07f, 0.52f), collar, Quaternion.identity);

            RoscoCompanion companion = rosco.AddComponent<RoscoCompanion>();
            SerializedObject serialized = new SerializedObject(companion);
            serialized.FindProperty("player").objectReferenceValue = GameObject.Find("Marcelo").transform;
            serialized.ApplyModifiedPropertiesWithoutUndo();
        }

        private static void CreateRoscoPart(
            PrimitiveType type,
            string name,
            Transform parent,
            Vector3 localPosition,
            Vector3 localScale,
            Color color,
            Quaternion rotation)
        {
            GameObject part = GameObject.CreatePrimitive(type);
            part.name = name;
            part.transform.SetParent(parent);
            part.transform.localPosition = localPosition;
            part.transform.localScale = localScale;
            part.transform.localRotation = rotation;
            part.GetComponent<Renderer>().sharedMaterial = MaterialFor(color);
            Object.DestroyImmediate(part.GetComponent<Collider>());
        }

        private static void CreateWorldController()
        {
            GameObject world = new GameObject("Park World Controller");
            ParkWorldController controller = world.AddComponent<ParkWorldController>();
            SerializedObject serialized = new SerializedObject(controller);
            serialized.FindProperty("sun").objectReferenceValue = Object.FindFirstObjectByType<Light>();
            serialized.ApplyModifiedPropertiesWithoutUndo();
        }

        private static void CreateAudioAtmosphere()
        {
            GameObject audio = new GameObject("XIV Audio Atmosphere");
            AudioSource source = audio.AddComponent<AudioSource>();
            source.playOnAwake = false;
            source.loop = true;
            source.spatialBlend = 0f;

            XIVAudioAtmosphere atmosphere = audio.AddComponent<XIVAudioAtmosphere>();
            SerializedObject serialized = new SerializedObject(atmosphere);
            serialized.FindProperty("musicSource").objectReferenceValue = source;
            serialized.FindProperty("worldController").objectReferenceValue = Object.FindFirstObjectByType<ParkWorldController>();
            serialized.ApplyModifiedPropertiesWithoutUndo();
        }

        private static void CreateWalkSession()
        {
            GameObject session = new GameObject("XIV Walk Session");
            XIVWalkSession walkSession = session.AddComponent<XIVWalkSession>();
            SerializedObject serialized = new SerializedObject(walkSession);
            serialized.FindProperty("player").objectReferenceValue = GameObject.Find("Marcelo").transform;
            serialized.FindProperty("rosco").objectReferenceValue = GameObject.Find("Rosco").GetComponent<RoscoCompanion>();
            serialized.FindProperty("atmosphere").objectReferenceValue = Object.FindFirstObjectByType<XIVAudioAtmosphere>();
            serialized.ApplyModifiedPropertiesWithoutUndo();
        }

        private static void CreateGreenMachineBoard()
        {
            GameObject district = GameObject.Find("Earnings Arcade");
            if (district == null) return;

            GameObject board = new GameObject("Green Machine Read Only Board");
            board.transform.SetParent(district.transform);
            board.transform.localPosition = new Vector3(0f, 2.7f, -4.2f);

            CreatePart(PrimitiveType.Cube, "Board Frame", board.transform, Vector3.zero, new Vector3(5.2f, 3.2f, 0.3f), new Color(0.025f, 0.045f, 0.06f));
            CreatePart(PrimitiveType.Cube, "Board Screen", board.transform, new Vector3(0f, 0f, -0.18f), new Vector3(4.7f, 2.7f, 0.08f), new Color(0.06f, 0.18f, 0.2f));

            GameObject textObject = new GameObject("Board Text");
            textObject.transform.SetParent(board.transform);
            textObject.transform.localPosition = new Vector3(-2.05f, 1.05f, -0.25f);
            TextMesh text = textObject.AddComponent<TextMesh>();
            text.text = "GREEN MACHINE\nLOCAL DATA\n\nOFFLINE BY DESIGN";
            text.anchor = TextAnchor.UpperLeft;
            text.alignment = TextAlignment.Left;
            text.characterSize = 0.19f;
            text.fontSize = 42;
            text.color = Color.white;

            LocalApiClient client = board.AddComponent<LocalApiClient>();
            GreenMachineBoard dataBoard = board.AddComponent<GreenMachineBoard>();
            SerializedObject serialized = new SerializedObject(dataBoard);
            serialized.FindProperty("apiClient").objectReferenceValue = client;
            serialized.FindProperty("display").objectReferenceValue = text;
            serialized.ApplyModifiedPropertiesWithoutUndo();
        }

        private static void CreateXivSystemsBoard()
        {
            GameObject district = GameObject.Find("Semiconductor Speedway");
            if (district == null) return;

            GameObject board = new GameObject("XIV Systems Board");
            board.transform.SetParent(district.transform);
            board.transform.localPosition = new Vector3(0f, 2.7f, -4.2f);

            CreatePart(PrimitiveType.Cube, "Systems Board Frame", board.transform, Vector3.zero, new Vector3(5.2f, 3.2f, 0.3f), new Color(0.025f, 0.045f, 0.06f));
            CreatePart(PrimitiveType.Cube, "Systems Board Screen", board.transform, new Vector3(0f, 0f, -0.18f), new Vector3(4.7f, 2.7f, 0.08f), new Color(0.08f, 0.14f, 0.25f));

            GameObject textObject = new GameObject("Systems Board Text");
            textObject.transform.SetParent(board.transform);
            textObject.transform.localPosition = new Vector3(-2.05f, 1.05f, -0.25f);
            TextMesh text = textObject.AddComponent<TextMesh>();
            text.text = "XIV\nSYSTEMS\n\nXIV          BUILDING\nMALOSOUND    MUSIC\nGREEN MACHINE  DATA\n\nLOCAL / EDITABLE";
            text.anchor = TextAnchor.UpperLeft;
            text.alignment = TextAlignment.Left;
            text.characterSize = 0.19f;
            text.fontSize = 42;
            text.color = Color.white;

            XIVSystemsBoard systemsBoard = board.AddComponent<XIVSystemsBoard>();
            SerializedObject serialized = new SerializedObject(systemsBoard);
            serialized.FindProperty("display").objectReferenceValue = text;
            serialized.ApplyModifiedPropertiesWithoutUndo();
        }

        private static void CreateFastTravel()
        {
            GameObject travel = new GameObject("Park Fast Travel");
            ParkFastTravel fastTravel = travel.AddComponent<ParkFastTravel>();
            SerializedObject serialized = new SerializedObject(fastTravel);
            serialized.FindProperty("player").objectReferenceValue = GameObject.Find("Marcelo").transform;
            serialized.FindProperty("rosco").objectReferenceValue = GameObject.Find("Rosco").GetComponent<RoscoCompanion>();
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
