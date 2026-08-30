using GreenMachine.Data;
using GreenMachine.Park;
using UnityEditor;
using UnityEditor.SceneManagement;
using Unity.AI.Navigation;
using UnityEngine;
using UnityEngine.AI;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace GreenMachine.Editor
{
    public static class GreenMachineParkBuilder
    {
        private const string GreenGateExportPath = "Assets/Art/Exports/GreenGate.fbx";
        private const string MarceloExportPath = "Assets/Art/Exports/MarceloHero.fbx";
        private const string SkyMaterialPath = "Assets/Art/Generated/XIVProceduralSky.mat";
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
            NavMeshSurface navigationSurface = ground.AddComponent<NavMeshSurface>();
            navigationSurface.collectObjects = CollectObjects.All;
            navigationSurface.useGeometry = NavMeshCollectGeometry.PhysicsColliders;

            foreach (var district in Districts) CreateDistrict(district.name, district.position, district.color);
            CreateWalkRoute();
            CreatePlayer();
            CreateRosco();
            CreateWorldController();
            CreateAudioAtmosphere();
            CreateRuntimeDiagnostics();
            CreatePauseController();
            CreateWalkSession();
            CreateWalkGuide();
            CreateGreenMachineBoard();
            CreateXivSystemsBoard();
            CreateFastTravel();
            navigationSurface.BuildNavMesh();
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

            CreateInterestPoint(route.transform, "Wind chime", new Vector3(3f, 0.3f, 12f), new Color(1f, 0.7f, 0.28f), "A small sound in the route. Rosco got here first.");
            CreateInterestPoint(route.transform, "Garden light", new Vector3(10f, 0.3f, 22f), new Color(0.36f, 0.86f, 0.72f), "The route changes when you keep moving.");
            CreateInterestPoint(route.transform, "Archive marker", new Vector3(16f, 0.3f, 30f), new Color(0.95f, 0.56f, 0.76f), "A place for songs, projects, and memories.");
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
            CreateRouteThreshold(parent, "Green Gate Departure", new Vector3(0f, 0f, 5f), new Vector3(3f, 0f, 12f));
            CreateRouteThreshold(parent, "First Walk Threshold", new Vector3(3f, 0f, 12f), new Vector3(10f, 0f, 22f));
            CreateRouteMarker(parent, "Route Marker One", new Vector3(10f, 0f, 22f), new Color(0.36f, 0.86f, 0.72f));
            CreateRouteMarker(parent, "Route Marker Two", new Vector3(16f, 0f, 30f), new Color(0.95f, 0.56f, 0.76f));
            CreateRouteWaystones(parent);
        }

        private static void CreateRouteWaystones(Transform parent)
        {
            Vector3[] waypoints =
            {
                new Vector3(0f, 0f, 5f),
                new Vector3(3f, 0f, 12f),
                new Vector3(10f, 0f, 22f),
                new Vector3(16f, 0f, 30f),
                new Vector3(16f, 0f, 34f),
            };
            Color[] colors =
            {
                new Color(0.88f, 0.96f, 0.34f),
                new Color(1f, 0.66f, 0.24f),
                new Color(0.36f, 0.86f, 0.72f),
                new Color(0.95f, 0.56f, 0.76f),
            };

            int waystoneIndex = 1;
            for (int segmentIndex = 0; segmentIndex < waypoints.Length - 1; segmentIndex++)
            {
                Vector3 direction = waypoints[segmentIndex + 1] - waypoints[segmentIndex];
                direction.y = 0f;
                float length = direction.magnitude;
                int count = Mathf.Max(1, Mathf.CeilToInt(length / 2.7f));
                for (int i = 0; i < count; i++)
                {
                    float t = (i + 0.5f) / count;
                    Vector3 position = Vector3.Lerp(waypoints[segmentIndex], waypoints[segmentIndex + 1], t);
                    Color color = Color.Lerp(colors[segmentIndex], colors[Mathf.Min(segmentIndex + 1, colors.Length - 1)], t);
                    CreateRouteWaystone(parent, $"Route Waystone {waystoneIndex++}", position, color, waystoneIndex * 0.43f);
                }
            }
        }

        private static void CreateRouteWaystone(Transform parent, string name, Vector3 position, Color color, float phaseOffset)
        {
            GameObject waystone = new GameObject(name);
            waystone.transform.SetParent(parent);
            waystone.transform.position = position;
            GameObject tile = CreatePart(PrimitiveType.Cylinder, "Waystone Tile", waystone.transform, new Vector3(0f, 0.08f, 0f), new Vector3(0.42f, 0.045f, 0.42f), new Color(0.12f, 0.16f, 0.15f));
            GameObject beacon = CreatePart(PrimitiveType.Sphere, "Waystone Beacon", waystone.transform, new Vector3(0f, 0.32f, 0f), new Vector3(0.16f, 0.16f, 0.16f), color);
            AddWindMotion(beacon, phaseOffset);
            CreatePointLight(waystone.transform, "Waystone Beacon Glow", new Vector3(0f, 0.3f, 0f), color);
            tile.GetComponent<Renderer>().sharedMaterial = MaterialFor(Color.Lerp(new Color(0.12f, 0.16f, 0.15f), color, 0.22f));
        }

        private static void CreateRouteThreshold(Transform parent, string name, Vector3 position, Vector3 nextPosition)
        {
            Vector3 direction = nextPosition - position;
            direction.y = 0f;
            GameObject threshold = new GameObject(name);
            threshold.transform.SetParent(parent);
            threshold.transform.position = position;
            threshold.transform.rotation = Quaternion.LookRotation(direction.normalized, Vector3.up);

            Color post = new Color(0.055f, 0.16f, 0.18f);
            Color trim = new Color(0.88f, 0.96f, 0.34f);
            Color warm = new Color(1f, 0.58f, 0.2f);
            CreatePart(PrimitiveType.Cylinder, "Threshold Post Left", threshold.transform, new Vector3(-2.15f, 1.9f, 0f), new Vector3(0.22f, 1.9f, 0.22f), post);
            CreatePart(PrimitiveType.Cylinder, "Threshold Post Right", threshold.transform, new Vector3(2.15f, 1.9f, 0f), new Vector3(0.22f, 1.9f, 0.22f), post);
            CreatePart(PrimitiveType.Cube, "Threshold Header", threshold.transform, new Vector3(0f, 3.75f, 0f), new Vector3(4.7f, 0.22f, 0.28f), trim);
            GameObject pennant = CreatePart(PrimitiveType.Cube, "Threshold Pennant", threshold.transform, new Vector3(0f, 3.35f, 0f), new Vector3(1.25f, 0.06f, 0.36f), warm);
            AddWindMotion(pennant, position.x * 0.1f + position.z * 0.04f);
            CreatePart(PrimitiveType.Sphere, "Threshold Light Left", threshold.transform, new Vector3(-2.15f, 3.95f, 0f), new Vector3(0.3f, 0.3f, 0.3f), warm);
            CreatePart(PrimitiveType.Sphere, "Threshold Light Right", threshold.transform, new Vector3(2.15f, 3.95f, 0f), new Vector3(0.3f, 0.3f, 0.3f), warm);
            CreatePointLight(threshold.transform, "Threshold Glow", new Vector3(0f, 3.35f, -0.25f), warm);
        }

        private static void CreateRouteMarker(Transform parent, string name, Vector3 position, Color color)
        {
            GameObject marker = new GameObject(name);
            marker.transform.SetParent(parent);
            marker.transform.position = position;
            CreatePart(PrimitiveType.Cylinder, "Marker Stem", marker.transform, new Vector3(0f, 0.8f, 0f), new Vector3(0.08f, 0.8f, 0.08f), new Color(0.08f, 0.1f, 0.12f));
            GameObject cap = CreatePart(PrimitiveType.Sphere, "Marker Light", marker.transform, new Vector3(0f, 1.75f, 0f), new Vector3(0.26f, 0.26f, 0.26f), color);
            AddWindMotion(cap, position.x * 0.07f + position.z * 0.03f);
            CreatePointLight(marker.transform, "Marker Glow", new Vector3(0f, 1.75f, 0f), color);
        }

        private static void CreateTree(Transform parent, string name, Vector3 position, float scale)
        {
            GameObject tree = new GameObject(name);
            tree.transform.SetParent(parent);
            tree.transform.localPosition = position;
            tree.transform.localScale = Vector3.one * scale;
            CreatePart(PrimitiveType.Cylinder, "Tree Trunk", tree.transform, new Vector3(0f, 1.1f, 0f), new Vector3(0.32f, 1.1f, 0.32f), new Color(0.28f, 0.12f, 0.06f));
            GameObject canopy = CreatePart(PrimitiveType.Sphere, "Tree Canopy", tree.transform, new Vector3(0f, 2.7f, 0f), new Vector3(1.35f, 1.7f, 1.35f), new Color(0.12f, 0.42f, 0.27f));
            AddWindMotion(canopy, position.x * 0.13f + position.z * 0.07f);
        }

        private static void CreateRouteLantern(Transform parent, string name, Vector3 position)
        {
            GameObject lantern = new GameObject(name);
            lantern.transform.SetParent(parent);
            lantern.transform.localPosition = position;
            CreatePart(PrimitiveType.Cylinder, "Lantern Post", lantern.transform, new Vector3(0f, 1.2f, 0f), new Vector3(0.12f, 1.2f, 0.12f), new Color(0.08f, 0.1f, 0.13f));
            GameObject lamp = CreatePart(PrimitiveType.Sphere, "Lantern", lantern.transform, new Vector3(0f, 2.45f, 0f), new Vector3(0.3f, 0.42f, 0.3f), new Color(1f, 0.66f, 0.24f));
            AddWindMotion(lamp, position.x * 0.1f + position.z * 0.05f);
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

        private static void CreateInterestPoint(Transform parent, string name, Vector3 position, Color color, string interactionMessage)
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
            XIVInteractable interactable = point.AddComponent<XIVInteractable>();
            SerializedObject interactionSerialized = new SerializedObject(interactable);
            interactionSerialized.FindProperty("interactionName").stringValue = name;
            interactionSerialized.FindProperty("message").stringValue = interactionMessage;
            interactionSerialized.FindProperty("visual").objectReferenceValue = point.GetComponent<Renderer>();
            interactionSerialized.ApplyModifiedPropertiesWithoutUndo();
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
            if (districtName == "Semiconductor Speedway")
            {
                CreateSemiconductorSpeedway(root.transform, color);
                return;
            }
            if (districtName == "Earnings Arcade")
            {
                CreateEarningsArcade(root.transform, color);
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

            CreateDistrictLabel(root.transform, districtName, 8f);
        }

        private static void CreateSemiconductorSpeedway(Transform parent, Color accentColor)
        {
            Color deck = new Color(0.035f, 0.09f, 0.15f);
            Color structure = new Color(0.06f, 0.16f, 0.22f);
            Color trim = Color.Lerp(accentColor, Color.white, 0.35f);

            CreatePart(PrimitiveType.Cylinder, "Speedway Deck", parent, new Vector3(0f, 0.22f, 0f), new Vector3(8f, 0.22f, 8f), deck);
            CreatePart(PrimitiveType.Cube, "Speedway Spine", parent, new Vector3(0f, 1.1f, 0f), new Vector3(1.15f, 1.1f, 9f), structure);
            CreatePart(PrimitiveType.Cube, "Speedway Rail Left", parent, new Vector3(-4.2f, 1.05f, 0f), new Vector3(0.28f, 1.05f, 7.2f), accentColor);
            CreatePart(PrimitiveType.Cube, "Speedway Rail Right", parent, new Vector3(4.2f, 1.05f, 0f), new Vector3(0.28f, 1.05f, 7.2f), accentColor);

            for (int i = -1; i <= 1; i++)
            {
                float x = i * 2.25f;
                CreatePart(PrimitiveType.Cube, $"Systems Module {i + 2}", parent, new Vector3(x, 1.05f, 2.65f), new Vector3(1.45f, 1.05f, 0.85f), structure);
                GameObject moduleLight = CreatePart(PrimitiveType.Sphere, $"Systems Module Light {i + 2}", parent, new Vector3(x, 2.2f, 2.65f), new Vector3(0.22f, 0.22f, 0.22f), trim);
                AddWindMotion(moduleLight, i * 0.8f);
            }

            CreatePart(PrimitiveType.Cylinder, "Systems Tower", parent, new Vector3(0f, 3.2f, 2.7f), new Vector3(1.5f, 3.2f, 1.5f), structure);
            GameObject towerBeacon = CreatePart(PrimitiveType.Sphere, "Systems Tower Beacon", parent, new Vector3(0f, 7.1f, 2.7f), new Vector3(0.75f, 0.75f, 0.75f), trim);
            AddWindMotion(towerBeacon, 1.7f);
            CreatePointLight(parent, "Systems Tower Glow", new Vector3(0f, 5.5f, 2.7f), accentColor);
            CreateDistrictLabel(parent, "Semiconductor Speedway", 8.2f);
        }

        private static void CreateEarningsArcade(Transform parent, Color accentColor)
        {
            Color floor = new Color(0.16f, 0.045f, 0.08f);
            Color structure = new Color(0.12f, 0.06f, 0.11f);
            Color screen = Color.Lerp(accentColor, Color.white, 0.28f);

            CreatePart(PrimitiveType.Cylinder, "Review Arcade Floor", parent, new Vector3(0f, 0.22f, 0f), new Vector3(8f, 0.22f, 8f), floor);
            CreatePart(PrimitiveType.Cube, "Review Arcade Back Wall", parent, new Vector3(0f, 3.1f, 3.8f), new Vector3(7.2f, 3.1f, 0.4f), structure);
            CreatePart(PrimitiveType.Cube, "Review Arcade Header", parent, new Vector3(0f, 6.3f, 3.55f), new Vector3(8.2f, 0.32f, 0.75f), accentColor);

            for (int i = -1; i <= 1; i++)
            {
                float x = i * 2.25f;
                CreatePart(PrimitiveType.Cube, $"Review Booth {i + 2}", parent, new Vector3(x, 1.45f, 1.8f), new Vector3(1.65f, 1.45f, 1.2f), structure);
                CreatePart(PrimitiveType.Cube, $"Review Screen {i + 2}", parent, new Vector3(x, 2.85f, 1.15f), new Vector3(1.25f, 0.78f, 0.1f), screen);
                GameObject boothLight = CreatePart(PrimitiveType.Sphere, $"Review Booth Light {i + 2}", parent, new Vector3(x, 3.85f, 1.75f), new Vector3(0.2f, 0.2f, 0.2f), screen);
                AddWindMotion(boothLight, i * 0.9f + 0.4f);
            }

            CreatePointLight(parent, "Review Arcade Glow", new Vector3(0f, 3.5f, 1.2f), accentColor);
            CreateDistrictLabel(parent, "Earnings Arcade", 8.2f);
        }

        private static void CreateDistrictLabel(Transform parent, string districtName, float height)
        {
            GameObject label = new GameObject("District Label");
            label.transform.SetParent(parent);
            label.transform.localPosition = new Vector3(0f, height, 0f);
            TextMesh text = label.AddComponent<TextMesh>();
            text.text = districtName;
            text.anchor = TextAnchor.MiddleCenter;
            text.characterSize = 0.12f;
            text.fontSize = 48;
            text.color = Color.white;
            label.AddComponent<XIVBillboard>();
        }

        private static void CreateGreenGate(Transform parent, Color accentColor)
        {
            if (TryCreateImportedGreenGate(parent, accentColor)) return;

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

            CreateGreenGateSign(parent);
        }

        private static bool TryCreateImportedGreenGate(Transform parent, Color accentColor)
        {
            // The Blender source carries authoring lights (energy 100) that overexpose the
            // runtime scene; the world's lighting is owned by the builder instead.
            if (AssetImporter.GetAtPath(GreenGateExportPath) is ModelImporter importer &&
                (importer.importLights || importer.importCameras))
            {
                importer.importLights = false;
                importer.importCameras = false;
                importer.SaveAndReimport();
            }

            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(GreenGateExportPath);
            if (prefab == null) return false;

            GameObject imported = PrefabUtility.InstantiatePrefab(prefab) as GameObject;
            if (imported == null) return false;

            imported.name = "Green Gate Imported Asset";
            imported.transform.SetParent(parent, false);
            imported.transform.localPosition = Vector3.zero;
            imported.transform.localRotation = Quaternion.identity;
            imported.transform.localScale = Vector3.one;
            RebindImportedMaterials(imported);
            CreatePointLight(parent, "Left Gate Glow", new Vector3(-4.2f, 4.3f, -1.8f), accentColor);
            CreatePointLight(parent, "Right Gate Glow", new Vector3(4.2f, 4.3f, -1.8f), new Color(0.92f, 0.35f, 0.34f));
            return true;
        }

        private static void RebindImportedMaterials(GameObject imported)
        {
            foreach (Renderer renderer in imported.GetComponentsInChildren<Renderer>(true))
            {
                Material[] sourceMaterials = renderer.sharedMaterials;
                Material[] replacementMaterials = new Material[sourceMaterials.Length];
                for (int i = 0; i < sourceMaterials.Length; i++)
                {
                    string materialName = sourceMaterials[i] != null ? sourceMaterials[i].name : string.Empty;
                    replacementMaterials[i] = MaterialFor(GreenGateMaterialColor(materialName));
                }

                renderer.sharedMaterials = replacementMaterials;
            }
        }

        private static Color GreenGateMaterialColor(string materialName)
        {
            if (materialName.Contains("Pine")) return new Color(0.035f, 0.19f, 0.15f);
            if (materialName.Contains("Signal Lime")) return new Color(0.62f, 0.95f, 0.13f);
            if (materialName.Contains("Coral")) return new Color(0.95f, 0.19f, 0.12f);
            if (materialName.Contains("Gold")) return new Color(1f, 0.58f, 0.07f);
            if (materialName.Contains("Cream")) return new Color(0.98f, 0.87f, 0.58f);
            if (materialName.Contains("Grass")) return new Color(0.08f, 0.42f, 0.20f);
            if (materialName.Contains("Wood")) return new Color(0.28f, 0.09f, 0.03f);
            if (materialName.Contains("Gate Stone")) return new Color(0.31f, 0.34f, 0.29f);
            if (materialName.Contains("Arrival Brick")) return new Color(0.56f, 0.20f, 0.10f);
            if (materialName.Contains("Patina Copper")) return new Color(0.08f, 0.38f, 0.29f);
            if (materialName.Contains("Parchment")) return new Color(0.92f, 0.74f, 0.38f);
            if (materialName.Contains("Lantern")) return new Color(1f, 0.58f, 0.07f);
            return new Color(0.12f, 0.22f, 0.2f);
        }

        private static void CreateGreenGateSign(Transform parent)
        {
            GameObject sign = new GameObject("XIV Gate Sign");
            sign.transform.SetParent(parent);
            sign.transform.localPosition = new Vector3(0f, 6.35f, -0.78f);
            TextMesh signText = sign.AddComponent<TextMesh>();
            signText.text = "XIV";
            signText.anchor = TextAnchor.MiddleCenter;
            signText.alignment = TextAlignment.Center;
            signText.characterSize = 0.16f;
            signText.fontSize = 72;
            signText.fontStyle = FontStyle.Bold;
            signText.color = Color.white;
            sign.AddComponent<XIVBillboard>();
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
            CreatePart(PrimitiveType.Cylinder, "Archive Garden Inner Ring", parent, new Vector3(0f, 0.48f, 0f), new Vector3(3.9f, 0.12f, 3.9f), new Color(0.13f, 0.31f, 0.28f));
            CreatePart(PrimitiveType.Cylinder, "Archive Memory Marker", parent, new Vector3(0f, 1.25f, 0f), new Vector3(0.65f, 1.25f, 0.65f), memory);
            GameObject memoryGlow = CreatePart(PrimitiveType.Sphere, "Archive Memory Glow", parent, new Vector3(0f, 3.1f, 0f), new Vector3(0.9f, 0.9f, 0.9f), accentColor);
            AddWindMotion(memoryGlow, 1.4f);
            CreatePointLight(parent, "Archive Garden Glow", new Vector3(0f, 2.7f, 0f), accentColor);

            CreateArchivePergola(parent, accentColor);
            CreateMemoryBench(parent, new Vector3(-3.1f, 0f, 0.2f), 90f);
            CreateMemoryBench(parent, new Vector3(3.1f, 0f, 0.2f), -90f);

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
            signText.characterSize = 0.14f;
            signText.fontSize = 48;
            signText.color = Color.white;
            sign.AddComponent<XIVBillboard>();

            GameObject summary = new GameObject("XIV Session Summary");
            summary.transform.SetParent(parent);
            summary.transform.localPosition = new Vector3(0f, 2.1f, -4.5f);
            TextMesh summaryText = summary.AddComponent<TextMesh>();
            summaryText.text = "ARCHIVE GARDEN\nWALK SAVES HERE";
            summaryText.anchor = TextAnchor.MiddleCenter;
            summaryText.alignment = TextAlignment.Center;
            summaryText.characterSize = 0.1f;
            summaryText.fontSize = 36;
            summaryText.color = Color.white;
            summary.AddComponent<XIVBillboard>();

            XIVSessionSummary sessionSummary = summary.AddComponent<XIVSessionSummary>();
            SerializedObject summarySerialized = new SerializedObject(sessionSummary);
            summarySerialized.FindProperty("display").objectReferenceValue = summaryText;
            summarySerialized.ApplyModifiedPropertiesWithoutUndo();

            GameObject archiveEntries = new GameObject("XIV Archive Entries");
            archiveEntries.transform.SetParent(parent);
            archiveEntries.transform.localPosition = new Vector3(0f, 4.1f, 4.35f);
            TextMesh archiveText = archiveEntries.AddComponent<TextMesh>();
            archiveText.text = "ARCHIVE GARDEN\n\nNO ENTRIES YET\n\nLOCAL / EDITABLE";
            archiveText.anchor = TextAnchor.MiddleCenter;
            archiveText.alignment = TextAlignment.Center;
            archiveText.characterSize = 0.085f;
            archiveText.fontSize = 34;
            archiveText.color = Color.white;
            archiveEntries.AddComponent<XIVBillboard>();

            XIVArchiveGarden archive = archiveEntries.AddComponent<XIVArchiveGarden>();
            SerializedObject archiveSerialized = new SerializedObject(archive);
            archiveSerialized.FindProperty("display").objectReferenceValue = archiveText;
            archiveSerialized.ApplyModifiedPropertiesWithoutUndo();
        }

        private static void CreateArchivePergola(Transform parent, Color accentColor)
        {
            GameObject pergola = new GameObject("Archive Garden Pergola");
            pergola.transform.SetParent(parent);
            pergola.transform.localPosition = new Vector3(0f, 0f, 2.7f);

            Color wood = new Color(0.18f, 0.1f, 0.07f);
            Color trim = Color.Lerp(accentColor, Color.white, 0.2f);
            CreatePart(PrimitiveType.Cylinder, "Pergola Post Left", pergola.transform, new Vector3(-3.6f, 1.45f, 0f), new Vector3(0.18f, 1.45f, 0.18f), wood);
            CreatePart(PrimitiveType.Cylinder, "Pergola Post Right", pergola.transform, new Vector3(3.6f, 1.45f, 0f), new Vector3(0.18f, 1.45f, 0.18f), wood);
            CreatePart(PrimitiveType.Cube, "Pergola Beam", pergola.transform, new Vector3(0f, 2.8f, 0f), new Vector3(7.4f, 0.2f, 0.28f), trim);
            for (int i = -2; i <= 2; i++)
            {
                GameObject slat = CreatePart(PrimitiveType.Cube, $"Pergola Slat {i + 3}", pergola.transform, new Vector3(i * 1.35f, 3.05f, 0f), new Vector3(0.1f, 0.08f, 0.9f), wood);
                AddWindMotion(slat, i * 0.55f);
            }

            CreatePart(PrimitiveType.Sphere, "Pergola Light Left", pergola.transform, new Vector3(-3.6f, 2.65f, -0.25f), new Vector3(0.28f, 0.28f, 0.28f), new Color(1f, 0.66f, 0.24f));
            CreatePart(PrimitiveType.Sphere, "Pergola Light Right", pergola.transform, new Vector3(3.6f, 2.65f, -0.25f), new Vector3(0.28f, 0.28f, 0.28f), new Color(1f, 0.66f, 0.24f));
        }

        private static void CreateMemoryBench(Transform parent, Vector3 position, float yaw)
        {
            GameObject bench = new GameObject("Archive Memory Bench");
            bench.transform.SetParent(parent);
            bench.transform.localPosition = position;
            bench.transform.localRotation = Quaternion.Euler(0f, yaw, 0f);
            Color wood = new Color(0.34f, 0.16f, 0.08f);
            Color metal = new Color(0.16f, 0.23f, 0.23f);
            CreatePart(PrimitiveType.Cube, "Bench Seat", bench.transform, new Vector3(0f, 0.7f, 0f), new Vector3(1.9f, 0.14f, 0.48f), wood);
            CreatePart(PrimitiveType.Cube, "Bench Back", bench.transform, new Vector3(0f, 1.1f, 0.22f), new Vector3(1.9f, 0.55f, 0.12f), wood);
            CreatePart(PrimitiveType.Cube, "Bench Leg Left", bench.transform, new Vector3(-0.65f, 0.34f, 0f), new Vector3(0.12f, 0.5f, 0.3f), metal);
            CreatePart(PrimitiveType.Cube, "Bench Leg Right", bench.transform, new Vector3(0.65f, 0.34f, 0f), new Vector3(0.12f, 0.5f, 0.3f), metal);
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

        private static void AddWindMotion(GameObject target, float phaseOffset)
        {
            XIVWindMotion motion = target.AddComponent<XIVWindMotion>();
            SerializedObject serialized = new SerializedObject(motion);
            serialized.FindProperty("phaseOffset").floatValue = phaseOffset;
            serialized.ApplyModifiedPropertiesWithoutUndo();
        }

        private static void CreatePointLight(Transform parent, string name, Vector3 localPosition, Color color)
        {
            GameObject lightObject = new GameObject(name);
            lightObject.transform.SetParent(parent);
            lightObject.transform.localPosition = localPosition;
            Light light = lightObject.AddComponent<Light>();
            light.type = LightType.Point;
            light.color = color;
            light.intensity = 0.55f;
            light.range = 7f;
        }

        private static void CreatePlayer()
        {
            GameObject player = new GameObject("Marcelo");
            player.name = "Marcelo";
            player.tag = "Player";
            player.transform.position = new Vector3(0f, 1f, -6f);
            player.AddComponent<CharacterController>();

            Transform body = null;
            Transform head = null;
            Transform armLeft = null;
            Transform armRight = null;
            Transform legLeft = null;
            Transform legRight = null;
            Transform shoulderLeft = null;
            Transform shoulderRight = null;
            Transform scarf = null;
            GameObject authoredModel = TryCreateImportedMarcelo(player.transform);
            if (authoredModel != null)
            {
                body = FindDescendant(authoredModel.transform, "Marcelo Body");
                head = FindDescendant(authoredModel.transform, "Marcelo Head");
                armLeft = FindDescendant(authoredModel.transform, "Marcelo Arm Left");
                armRight = FindDescendant(authoredModel.transform, "Marcelo Arm Right");
                legLeft = FindDescendant(authoredModel.transform, "Marcelo Leg Left");
                legRight = FindDescendant(authoredModel.transform, "Marcelo Leg Right");
                shoulderLeft = FindDescendant(authoredModel.transform, "Marcelo Shoulder Left");
                shoulderRight = FindDescendant(authoredModel.transform, "Marcelo Shoulder Right");
                scarf = FindDescendant(authoredModel.transform, "Marcelo Scarf");
                if (body == null || head == null || armLeft == null || armRight == null ||
                    legLeft == null || legRight == null || shoulderLeft == null ||
                    shoulderRight == null || scarf == null)
                {
                    Object.DestroyImmediate(authoredModel);
                    authoredModel = null;
                }
            }

            if (authoredModel == null)
            {
                Color coat = new Color(0.05f, 0.23f, 0.24f);
                Color shirt = new Color(0.9f, 0.62f, 0.18f);
                Color skin = new Color(0.75f, 0.42f, 0.25f);
                Color hair = new Color(0.035f, 0.022f, 0.018f);
                Color dark = new Color(0.025f, 0.035f, 0.045f);
                Color boot = new Color(0.12f, 0.08f, 0.06f);
                Color accent = new Color(0.88f, 0.96f, 0.34f);
                Color metal = new Color(0.72f, 0.46f, 0.16f);

                // The fallback keeps a connected human silhouette until the authored FBX is available.
                body = CreatePlayerPart(PrimitiveType.Capsule, "Marcelo Body", player.transform, new Vector3(0f, 1.33f, 0f), new Vector3(0.7f, 0.82f, 0.5f), coat, Quaternion.identity).transform;
                CreatePlayerPart(PrimitiveType.Sphere, "Marcelo Waist", player.transform, new Vector3(0f, 0.67f, 0f), new Vector3(0.62f, 0.34f, 0.44f), dark, Quaternion.identity);
                CreatePlayerPart(PrimitiveType.Cube, "Marcelo Shirt", player.transform, new Vector3(0f, 1.34f, 0.43f), new Vector3(0.42f, 0.6f, 0.08f), shirt, Quaternion.identity);
                CreatePlayerPart(PrimitiveType.Cube, "Marcelo Coat Trim", player.transform, new Vector3(0f, 1.34f, 0.49f), new Vector3(0.07f, 0.68f, 0.04f), accent, Quaternion.identity);
                CreatePlayerPart(PrimitiveType.Cube, "Marcelo Belt", player.transform, new Vector3(0f, 0.86f, 0.02f), new Vector3(0.62f, 0.1f, 0.48f), metal, Quaternion.identity);
                head = CreatePlayerPart(PrimitiveType.Sphere, "Marcelo Head", player.transform, new Vector3(0f, 2.38f, 0.03f), new Vector3(0.56f, 0.64f, 0.54f), skin, Quaternion.identity).transform;
                CreatePlayerPart(PrimitiveType.Cylinder, "Marcelo Neck", player.transform, new Vector3(0f, 1.96f, 0f), new Vector3(0.2f, 0.16f, 0.2f), skin, Quaternion.identity);
                CreatePlayerPart(PrimitiveType.Sphere, "Marcelo Hair", player.transform, new Vector3(0f, 2.65f, -0.01f), new Vector3(0.58f, 0.28f, 0.56f), hair, Quaternion.identity);
                CreatePlayerPart(PrimitiveType.Cube, "Marcelo Cap Brim", player.transform, new Vector3(0f, 2.58f, 0.34f), new Vector3(0.56f, 0.07f, 0.3f), hair, Quaternion.identity);
                CreatePlayerPart(PrimitiveType.Sphere, "Marcelo Eye Left", player.transform, new Vector3(-0.18f, 2.4f, 0.48f), new Vector3(0.07f, 0.08f, 0.04f), dark, Quaternion.identity);
                CreatePlayerPart(PrimitiveType.Sphere, "Marcelo Eye Right", player.transform, new Vector3(0.18f, 2.4f, 0.48f), new Vector3(0.07f, 0.08f, 0.04f), dark, Quaternion.identity);

                shoulderLeft = CreatePlayerPart(PrimitiveType.Sphere, "Marcelo Shoulder Left", player.transform, new Vector3(-0.56f, 1.78f, 0f), new Vector3(0.34f, 0.3f, 0.38f), coat, Quaternion.identity).transform;
                shoulderRight = CreatePlayerPart(PrimitiveType.Sphere, "Marcelo Shoulder Right", player.transform, new Vector3(0.56f, 1.78f, 0f), new Vector3(0.34f, 0.3f, 0.38f), coat, Quaternion.identity).transform;
                armLeft = CreatePlayerPart(PrimitiveType.Capsule, "Marcelo Arm Left", player.transform, new Vector3(-0.66f, 1.36f, 0f), new Vector3(0.18f, 0.54f, 0.18f), coat, Quaternion.Euler(0f, 0f, -14f)).transform;
                armRight = CreatePlayerPart(PrimitiveType.Capsule, "Marcelo Arm Right", player.transform, new Vector3(0.66f, 1.36f, 0f), new Vector3(0.18f, 0.54f, 0.18f), coat, Quaternion.Euler(0f, 0f, 14f)).transform;
                CreatePlayerPart(PrimitiveType.Sphere, "Marcelo Hand Left", player.transform, new Vector3(-0.76f, 0.84f, 0f), new Vector3(0.2f, 0.22f, 0.2f), skin, Quaternion.identity);
                CreatePlayerPart(PrimitiveType.Sphere, "Marcelo Hand Right", player.transform, new Vector3(0.76f, 0.84f, 0f), new Vector3(0.2f, 0.22f, 0.2f), skin, Quaternion.identity);
                legLeft = CreatePlayerPart(PrimitiveType.Capsule, "Marcelo Leg Left", player.transform, new Vector3(-0.25f, 0.35f, 0f), new Vector3(0.23f, 0.58f, 0.23f), dark, Quaternion.identity).transform;
                legRight = CreatePlayerPart(PrimitiveType.Capsule, "Marcelo Leg Right", player.transform, new Vector3(0.25f, 0.35f, 0f), new Vector3(0.23f, 0.58f, 0.23f), dark, Quaternion.identity).transform;
                CreatePlayerPart(PrimitiveType.Cube, "Marcelo Boot Left", player.transform, new Vector3(-0.25f, -0.03f, 0.15f), new Vector3(0.38f, 0.18f, 0.58f), boot, Quaternion.identity);
                CreatePlayerPart(PrimitiveType.Cube, "Marcelo Boot Right", player.transform, new Vector3(0.25f, -0.03f, 0.15f), new Vector3(0.38f, 0.18f, 0.58f), boot, Quaternion.identity);
                CreatePlayerPart(PrimitiveType.Cube, "Marcelo Backpack", player.transform, new Vector3(0f, 1.42f, -0.46f), new Vector3(0.66f, 0.74f, 0.22f), shirt, Quaternion.identity);
                scarf = CreatePlayerPart(PrimitiveType.Cube, "Marcelo Scarf", player.transform, new Vector3(0f, 1.86f, 0.03f), new Vector3(0.5f, 0.12f, 0.34f), accent, Quaternion.identity).transform;
                CreatePlayerPart(PrimitiveType.Cube, "Marcelo Scarf Tail", player.transform, new Vector3(0.25f, 1.57f, -0.02f), new Vector3(0.12f, 0.56f, 0.08f), accent, Quaternion.Euler(0f, 0f, -10f));
            }

            Camera camera = Camera.main;
            camera.transform.position = player.transform.position + new Vector3(0f, 5f, -8f);
            camera.transform.LookAt(player.transform.position + Vector3.up * 1.4f);
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.025f, 0.045f, 0.075f);
            ThirdPersonCamera followCamera = camera.gameObject.AddComponent<ThirdPersonCamera>();
            SerializedObject cameraSerialized = new SerializedObject(followCamera);
            cameraSerialized.FindProperty("target").objectReferenceValue = player.transform;
            cameraSerialized.ApplyModifiedPropertiesWithoutUndo();
            ThirdPersonMover mover = player.AddComponent<ThirdPersonMover>();
            SerializedObject serialized = new SerializedObject(mover);
            serialized.FindProperty("cameraTransform").objectReferenceValue = camera.transform;
            serialized.ApplyModifiedPropertiesWithoutUndo();

            MarceloProceduralAnimator animator = player.AddComponent<MarceloProceduralAnimator>();
            SerializedObject animatorSerialized = new SerializedObject(animator);
            animatorSerialized.FindProperty("mover").objectReferenceValue = mover;
            animatorSerialized.FindProperty("body").objectReferenceValue = body;
            animatorSerialized.FindProperty("head").objectReferenceValue = head;
            animatorSerialized.FindProperty("armLeft").objectReferenceValue = armLeft;
            animatorSerialized.FindProperty("armRight").objectReferenceValue = armRight;
            animatorSerialized.FindProperty("legLeft").objectReferenceValue = legLeft;
            animatorSerialized.FindProperty("legRight").objectReferenceValue = legRight;
            animatorSerialized.FindProperty("shoulderLeft").objectReferenceValue = shoulderLeft;
            animatorSerialized.FindProperty("shoulderRight").objectReferenceValue = shoulderRight;
            animatorSerialized.FindProperty("scarf").objectReferenceValue = scarf;
            animatorSerialized.ApplyModifiedPropertiesWithoutUndo();
            player.AddComponent<XIVInteractionController>();
        }

        private static GameObject TryCreateImportedMarcelo(Transform parent)
        {
            if (AssetImporter.GetAtPath(MarceloExportPath) is ModelImporter importer &&
                (importer.importLights || importer.importCameras))
            {
                importer.importLights = false;
                importer.importCameras = false;
                importer.SaveAndReimport();
            }

            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(MarceloExportPath);
            if (prefab == null) return null;

            GameObject imported = PrefabUtility.InstantiatePrefab(prefab) as GameObject;
            if (imported == null) return null;

            imported.name = "Marcelo Authored Model";
            imported.transform.SetParent(parent, false);
            imported.transform.localPosition = Vector3.zero;
            imported.transform.localRotation = Quaternion.identity;
            imported.transform.localScale = Vector3.one;
            return imported;
        }

        private static Transform FindDescendant(Transform root, string name)
        {
            if (root == null) return null;
            if (root.name == name) return root;
            foreach (Transform child in root)
            {
                Transform result = FindDescendant(child, name);
                if (result != null) return result;
            }

            return null;
        }

        private static GameObject CreatePlayerPart(
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
            return part;
        }

        private static void CreateRosco()
        {
            GameObject rosco = new GameObject("Rosco");
            rosco.transform.position = new Vector3(-2f, 0.18f, -8f);
            NavMeshAgent navigationAgent = rosco.AddComponent<NavMeshAgent>();
            navigationAgent.speed = 4.2f;
            navigationAgent.acceleration = 16f;
            navigationAgent.angularSpeed = 720f;
            navigationAgent.radius = 0.55f;
            navigationAgent.height = 2.2f;
            navigationAgent.updatePosition = false;
            navigationAgent.updateRotation = false;
            // Serialized disabled: RoscoCompanion enables it once a valid NavMesh is loaded,
            // preventing the "Failed to create agent" error at scene load.
            navigationAgent.enabled = false;

            Color fur = new Color(0.56f, 0.27f, 0.12f);
            Color lightFur = new Color(0.82f, 0.58f, 0.34f);
            Color dark = new Color(0.025f, 0.018f, 0.015f);
            Color collar = new Color(0.92f, 0.25f, 0.28f);

            GameObject body = CreateRoscoPart(PrimitiveType.Sphere, "Rosco Body", rosco.transform, new Vector3(0f, 0.9f, 0f), new Vector3(1.25f, 0.78f, 1.55f), fur, Quaternion.identity);
            GameObject head = CreateRoscoPart(PrimitiveType.Sphere, "Rosco Head", rosco.transform, new Vector3(0f, 1.45f, 0.95f), new Vector3(0.92f, 0.86f, 0.9f), fur, Quaternion.identity);
            CreateRoscoPart(PrimitiveType.Sphere, "Rosco Muzzle", rosco.transform, new Vector3(0f, 1.25f, 1.62f), new Vector3(0.5f, 0.34f, 0.42f), lightFur, Quaternion.identity);
            CreateRoscoPart(PrimitiveType.Sphere, "Rosco Nose", rosco.transform, new Vector3(0f, 1.3f, 1.98f), new Vector3(0.18f, 0.14f, 0.14f), dark, Quaternion.identity);

            GameObject earLeft = CreateRoscoPart(PrimitiveType.Capsule, "Rosco Ear Left", rosco.transform, new Vector3(-0.48f, 1.9f, 0.82f), new Vector3(0.28f, 0.62f, 0.24f), fur, Quaternion.Euler(0f, 0f, -18f));
            GameObject earRight = CreateRoscoPart(PrimitiveType.Capsule, "Rosco Ear Right", rosco.transform, new Vector3(0.48f, 1.9f, 0.82f), new Vector3(0.28f, 0.62f, 0.24f), fur, Quaternion.Euler(0f, 0f, 18f));
            CreateRoscoPart(PrimitiveType.Sphere, "Rosco Eye Left", rosco.transform, new Vector3(-0.31f, 1.62f, 1.68f), new Vector3(0.1f, 0.12f, 0.08f), dark, Quaternion.identity);
            CreateRoscoPart(PrimitiveType.Sphere, "Rosco Eye Right", rosco.transform, new Vector3(0.31f, 1.62f, 1.68f), new Vector3(0.1f, 0.12f, 0.08f), dark, Quaternion.identity);

            GameObject frontLegLeft = CreateRoscoPart(PrimitiveType.Capsule, "Rosco Front Leg Left", rosco.transform, new Vector3(-0.43f, 0.38f, 0.62f), new Vector3(0.25f, 0.55f, 0.25f), lightFur, Quaternion.identity);
            GameObject frontLegRight = CreateRoscoPart(PrimitiveType.Capsule, "Rosco Front Leg Right", rosco.transform, new Vector3(0.43f, 0.38f, 0.62f), new Vector3(0.25f, 0.55f, 0.25f), lightFur, Quaternion.identity);
            GameObject backLegLeft = CreateRoscoPart(PrimitiveType.Capsule, "Rosco Back Leg Left", rosco.transform, new Vector3(-0.43f, 0.38f, -0.58f), new Vector3(0.28f, 0.6f, 0.28f), fur, Quaternion.identity);
            GameObject backLegRight = CreateRoscoPart(PrimitiveType.Capsule, "Rosco Back Leg Right", rosco.transform, new Vector3(0.43f, 0.38f, -0.58f), new Vector3(0.28f, 0.6f, 0.28f), fur, Quaternion.identity);
            GameObject tail = CreateRoscoPart(PrimitiveType.Capsule, "Rosco Tail", rosco.transform, new Vector3(0f, 1.08f, -1.25f), new Vector3(0.2f, 0.72f, 0.2f), lightFur, Quaternion.Euler(-35f, 0f, 0f));
            CreateRoscoPart(PrimitiveType.Cylinder, "Rosco Collar", rosco.transform, new Vector3(0f, 1.62f, 0.92f), new Vector3(0.52f, 0.07f, 0.52f), collar, Quaternion.identity);

            RoscoCompanion companion = rosco.AddComponent<RoscoCompanion>();
            SerializedObject serialized = new SerializedObject(companion);
            serialized.FindProperty("player").objectReferenceValue = GameObject.Find("Marcelo").transform;
            serialized.ApplyModifiedPropertiesWithoutUndo();

            RoscoProceduralAnimator animator = rosco.AddComponent<RoscoProceduralAnimator>();
            SerializedObject animatorSerialized = new SerializedObject(animator);
            animatorSerialized.FindProperty("companion").objectReferenceValue = companion;
            animatorSerialized.FindProperty("body").objectReferenceValue = body.transform;
            animatorSerialized.FindProperty("head").objectReferenceValue = head.transform;
            animatorSerialized.FindProperty("earLeft").objectReferenceValue = earLeft.transform;
            animatorSerialized.FindProperty("earRight").objectReferenceValue = earRight.transform;
            animatorSerialized.FindProperty("frontLegLeft").objectReferenceValue = frontLegLeft.transform;
            animatorSerialized.FindProperty("frontLegRight").objectReferenceValue = frontLegRight.transform;
            animatorSerialized.FindProperty("backLegLeft").objectReferenceValue = backLegLeft.transform;
            animatorSerialized.FindProperty("backLegRight").objectReferenceValue = backLegRight.transform;
            animatorSerialized.FindProperty("tail").objectReferenceValue = tail.transform;
            animatorSerialized.ApplyModifiedPropertiesWithoutUndo();

            ThirdPersonCamera followCamera = Camera.main != null ? Camera.main.GetComponent<ThirdPersonCamera>() : null;
            if (followCamera != null)
            {
                SerializedObject cameraSerialized = new SerializedObject(followCamera);
                cameraSerialized.FindProperty("secondaryTarget").objectReferenceValue = rosco.transform;
                cameraSerialized.ApplyModifiedPropertiesWithoutUndo();
            }
        }

        private static GameObject CreateRoscoPart(
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
            return part;
        }

        private static void CreateWorldController()
        {
            GameObject world = new GameObject("Park World Controller");
            ParkWorldController controller = world.AddComponent<ParkWorldController>();
            Material skyMaterial = CreateSkyMaterial();
            RenderSettings.skybox = skyMaterial;
            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.1f, 0.15f, 0.17f);
            RenderSettings.ambientIntensity = 0.45f;
            RenderSettings.reflectionIntensity = 0.25f;
            RenderSettings.fog = true;
            RenderSettings.fogMode = FogMode.ExponentialSquared;
            RenderSettings.fogColor = new Color(0.08f, 0.14f, 0.18f);
            RenderSettings.fogDensity = 0.008f;
            SerializedObject serialized = new SerializedObject(controller);
            serialized.FindProperty("sun").objectReferenceValue = FindWorldSun();
            serialized.FindProperty("skyMaterial").objectReferenceValue = skyMaterial;
            serialized.ApplyModifiedPropertiesWithoutUndo();
        }

        private static Light FindWorldSun()
        {
            foreach (Light light in Object.FindObjectsByType<Light>(FindObjectsSortMode.None))
            {
                if (light.type == LightType.Directional)
                {
                    light.color = new Color(1f, 0.93f, 0.82f);
                    light.intensity = 1f;
                    light.shadows = LightShadows.Soft;
                    return light;
                }
            }

            Debug.LogWarning("XIV world has no directional light to use as the sun.");
            return null;
        }

        private static Material CreateSkyMaterial()
        {
            if (!AssetDatabase.IsValidFolder("Assets/Art/Generated"))
            {
                if (!AssetDatabase.IsValidFolder("Assets/Art")) AssetDatabase.CreateFolder("Assets", "Art");
                AssetDatabase.CreateFolder("Assets/Art", "Generated");
            }

            Material skyMaterial = AssetDatabase.LoadAssetAtPath<Material>(SkyMaterialPath);
            if (skyMaterial == null)
            {
                Shader skyShader = Shader.Find("Skybox/Procedural");
                if (skyShader == null)
                {
                    Debug.LogError("XIV could not find the Skybox/Procedural shader.");
                    return null;
                }

                skyMaterial = new Material(skyShader) { name = "XIV Procedural Sky" };
                AssetDatabase.CreateAsset(skyMaterial, SkyMaterialPath);
            }

            if (skyMaterial.HasProperty("_SkyTint")) skyMaterial.SetColor("_SkyTint", new Color(0.18f, 0.36f, 0.48f));
            if (skyMaterial.HasProperty("_GroundColor")) skyMaterial.SetColor("_GroundColor", new Color(0.08f, 0.14f, 0.15f));
            if (skyMaterial.HasProperty("_Exposure")) skyMaterial.SetFloat("_Exposure", 0.85f);
            EditorUtility.SetDirty(skyMaterial);
            AssetDatabase.SaveAssets();
            return skyMaterial;
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

        private static void CreateRuntimeDiagnostics()
        {
            GameObject diagnostics = new GameObject("XIV Runtime Diagnostics");
            diagnostics.AddComponent<XIVRuntimeDiagnostics>();
        }

        private static void CreatePauseController()
        {
            GameObject pause = new GameObject("XIV Pause Controller");
            pause.AddComponent<XIVPauseController>();
        }

        private static void CreateWalkSession()
        {
            GameObject session = new GameObject("XIV Walk Session");
            XIVWalkSession walkSession = session.AddComponent<XIVWalkSession>();
            SerializedObject serialized = new SerializedObject(walkSession);
            serialized.FindProperty("player").objectReferenceValue = GameObject.Find("Marcelo").transform;
            serialized.FindProperty("rosco").objectReferenceValue = GameObject.Find("Rosco").GetComponent<RoscoCompanion>();
            serialized.FindProperty("atmosphere").objectReferenceValue = Object.FindFirstObjectByType<XIVAudioAtmosphere>();
            serialized.FindProperty("interactionController").objectReferenceValue = GameObject.Find("Marcelo").GetComponent<XIVInteractionController>();
            serialized.ApplyModifiedPropertiesWithoutUndo();
        }

        private static void CreateWalkGuide()
        {
            GameObject gate = GameObject.Find("Green Gate");
            if (gate == null) return;

            GameObject guide = new GameObject("XIV Walk Guide");
            guide.transform.SetParent(gate.transform);
            guide.transform.localPosition = new Vector3(0f, 3.2f, -3.7f);
            TextMesh text = guide.AddComponent<TextMesh>();
            text.text = "ARCHIVE GARDEN ->\nWALK WITH ROSCO";
            text.anchor = TextAnchor.MiddleCenter;
            text.alignment = TextAlignment.Center;
            text.characterSize = 0.12f;
            text.fontSize = 42;
            text.color = Color.white;
            guide.AddComponent<XIVBillboard>();

            XIVWalkGuide walkGuide = guide.AddComponent<XIVWalkGuide>();
            SerializedObject serialized = new SerializedObject(walkGuide);
            serialized.FindProperty("display").objectReferenceValue = text;
            serialized.FindProperty("session").objectReferenceValue = GameObject.Find("XIV Walk Session").GetComponent<XIVWalkSession>();
            serialized.FindProperty("rosco").objectReferenceValue = GameObject.Find("Rosco").GetComponent<RoscoCompanion>();
            serialized.FindProperty("player").objectReferenceValue = GameObject.Find("Marcelo").transform;
            serialized.FindProperty("destination").objectReferenceValue = GameObject.Find("Archive Garden").transform;
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
            text.characterSize = 0.085f;
            text.fontSize = 42;
            text.color = Color.white;
            textObject.AddComponent<XIVBillboard>();

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
            text.characterSize = 0.085f;
            text.fontSize = 42;
            text.color = Color.white;
            textObject.AddComponent<XIVBillboard>();

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
            Shader shader = Shader.Find("Standard");
            if (shader == null) shader = Shader.Find("Universal Render Pipeline/Lit");
            Material material = new Material(shader);
            material.color = color;
            if (material.HasProperty("_BaseColor")) material.SetColor("_BaseColor", color);
            return material;
        }
    }
}
