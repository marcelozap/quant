using UnityEngine;
using UnityEngine.InputSystem;

namespace GreenMachine.Park
{
    public sealed class XIVPauseController : MonoBehaviour
    {
        [SerializeField] private bool pauseOnFocusLoss = true;

        private bool paused;
        private float previousTimeScale = 1f;
        private bool previousAudioPause;
        private GUIStyle titleStyle;
        private GUIStyle subtitleStyle;

        public bool IsPaused => paused;

        private void Update()
        {
            if (Keyboard.current != null && Keyboard.current.escapeKey.wasPressedThisFrame)
            {
                SetPaused(!paused);
            }
        }

        public void SetPaused(bool value)
        {
            if (paused == value) return;

            if (value)
            {
                previousTimeScale = Time.timeScale;
                previousAudioPause = AudioListener.pause;
                paused = true;
                Time.timeScale = 0f;
                AudioListener.pause = true;
                return;
            }

            paused = false;
            Time.timeScale = previousTimeScale > 0f ? previousTimeScale : 1f;
            AudioListener.pause = previousAudioPause;
        }

        private void OnApplicationFocus(bool hasFocus)
        {
            if (!hasFocus && pauseOnFocusLoss) SetPaused(true);
        }

        private void OnDestroy()
        {
            if (paused) SetPaused(false);
        }

        private void OnGUI()
        {
            if (!paused) return;

            EnsureStyles();
            Color previousColor = GUI.color;
            GUI.color = new Color(0.015f, 0.025f, 0.04f, 0.92f);
            GUI.Box(new Rect(Screen.width * 0.5f - 180f, Screen.height * 0.5f - 90f, 360f, 180f), GUIContent.none);
            GUI.color = Color.white;
            GUI.Label(new Rect(Screen.width * 0.5f - 140f, Screen.height * 0.5f - 60f, 280f, 42f), "XIV", titleStyle);
            GUI.Label(new Rect(Screen.width * 0.5f - 140f, Screen.height * 0.5f - 8f, 280f, 34f), "PAUSED", subtitleStyle);
            GUI.color = previousColor;
        }

        private void EnsureStyles()
        {
            if (titleStyle != null) return;

            titleStyle = new GUIStyle(GUI.skin.label)
            {
                alignment = TextAnchor.MiddleCenter,
                fontSize = 28,
                fontStyle = FontStyle.Bold,
            };
            subtitleStyle = new GUIStyle(GUI.skin.label)
            {
                alignment = TextAnchor.MiddleCenter,
                fontSize = 18,
                fontStyle = FontStyle.Normal,
            };
        }
    }
}
