using System.IO;
using UnityEditor;
using UnityEditor.Build.Reporting;

namespace GreenMachine.Editor
{
    public static class XIVPrivateBuild
    {
        private const string ScenePath = "Assets/Scenes/XIVWorld.unity";
        private const string ProductName = "XIV";
        private const string CompanyName = "Marcelo Zapata";
        private const string BundleVersion = "0.1.0";
        private static string ProjectRootPath => Directory.GetParent(UnityEngine.Application.dataPath).FullName;
        private static string OutputFileSystemPath => Path.Combine(ProjectRootPath, "Builds", "XIV", "XIV.app");

        [MenuItem("XIV/Build Private macOS App")]
        public static void BuildMacApp()
        {
            if (BuildMacAppInternal())
            {
                UnityEngine.Debug.Log($"XIV build succeeded: {OutputFileSystemPath}");
            }
        }

        public static void BuildPrivateMacAppBatch()
        {
            bool success = BuildMacAppInternal();
            EditorApplication.Exit(success ? 0 : 1);
        }

        private static bool BuildMacAppInternal()
        {
            if (AssetDatabase.LoadAssetAtPath<SceneAsset>(ScenePath) == null)
            {
                UnityEngine.Debug.LogError($"XIV build failed: {ScenePath} does not exist. Run XIV/Create First Playable World first.");
                return false;
            }

            if (!XIVWorldValidator.ValidateFirstWorldScene()) return false;

            ConfigurePrivateBuild();
            EditorBuildSettings.scenes = new[]
            {
                new EditorBuildSettingsScene(ScenePath, true),
            };
            Directory.CreateDirectory(Path.GetDirectoryName(OutputFileSystemPath));

            BuildReport report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                scenes = new[] { ScenePath },
                locationPathName = OutputFileSystemPath,
                target = BuildTarget.StandaloneOSX,
                options = BuildOptions.None,
            });

            if (report.summary.result == BuildResult.Succeeded) return true;
            UnityEngine.Debug.LogError($"XIV build failed: {report.summary.result}. Errors: {report.summary.totalErrors}.");
            return false;
        }

        private static void ConfigurePrivateBuild()
        {
            PlayerSettings.productName = ProductName;
            PlayerSettings.companyName = CompanyName;
            PlayerSettings.bundleVersion = BundleVersion;
            PlayerSettings.runInBackground = false;
        }
    }
}
