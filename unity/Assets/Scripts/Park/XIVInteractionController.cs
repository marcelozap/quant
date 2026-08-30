using System;
using UnityEngine;
using UnityEngine.InputSystem;

namespace GreenMachine.Park
{
    [RequireComponent(typeof(ThirdPersonMover))]
    public sealed class XIVInteractionController : MonoBehaviour
    {
        [SerializeField] [Min(0.5f)] private float interactionRadius = 3f;
        [SerializeField] private XIVPauseController pauseController;

        private XIVInteractable[] interactables = Array.Empty<XIVInteractable>();
        private XIVInteractable currentTarget;
        private string feedbackTitle = string.Empty;
        private string feedbackMessage = string.Empty;
        private float feedbackTimer;
        private GUIStyle panelStyle;
        private GUIStyle titleStyle;
        private GUIStyle bodyStyle;

        public event Action<string> InteractionPerformed;
        public XIVInteractable CurrentTarget => currentTarget;

        private void Start()
        {
            interactables = FindObjectsByType<XIVInteractable>(FindObjectsSortMode.None);
            if (pauseController == null) pauseController = FindFirstObjectByType<XIVPauseController>();
        }

        private void Update()
        {
            if (feedbackTimer > 0f) feedbackTimer -= Time.deltaTime;
            if (pauseController != null && pauseController.IsPaused) return;

            currentTarget = FindClosestTarget();
            if (Keyboard.current == null || !Keyboard.current.eKey.wasPressedThisFrame || currentTarget == null) return;
            if (!currentTarget.TryInteract()) return;

            feedbackTitle = currentTarget.InteractionName.ToUpperInvariant();
            feedbackMessage = currentTarget.Message;
            feedbackTimer = 4f;
            InteractionPerformed?.Invoke(currentTarget.InteractionName);
        }

        private XIVInteractable FindClosestTarget()
        {
            XIVInteractable closest = null;
            float closestDistance = interactionRadius;
            foreach (XIVInteractable interactable in interactables)
            {
                if (interactable == null || !interactable.isActiveAndEnabled || !interactable.CanInteract) continue;
                float distance = Vector3.Distance(transform.position, interactable.FocusPosition);
                if (distance <= closestDistance)
                {
                    closest = interactable;
                    closestDistance = distance;
                }
            }

            return closest;
        }

        private void OnGUI()
        {
            if (feedbackTimer <= 0f && currentTarget == null) return;

            EnsureStyles();
            float width = Mathf.Min(460f, Screen.width - 40f);
            float height = feedbackTimer > 0f ? 116f : 64f;
            Rect panel = new Rect((Screen.width - width) * 0.5f, Screen.height - height - 28f, width, height);
            Color previousColor = GUI.color;
            GUI.color = new Color(0.015f, 0.025f, 0.04f, 0.92f);
            GUI.Box(panel, GUIContent.none, panelStyle);
            GUI.color = Color.white;

            if (feedbackTimer > 0f)
            {
                GUI.Label(new Rect(panel.x + 18f, panel.y + 12f, panel.width - 36f, 26f), feedbackTitle, titleStyle);
                GUI.Label(new Rect(panel.x + 18f, panel.y + 40f, panel.width - 36f, panel.height - 48f), feedbackMessage, bodyStyle);
            }
            else
            {
                GUI.Label(new Rect(panel.x + 18f, panel.y + 15f, panel.width - 36f, 32f), $"E   {currentTarget.InteractionName.ToUpperInvariant()}", titleStyle);
            }

            GUI.color = previousColor;
        }

        private void EnsureStyles()
        {
            if (panelStyle != null) return;

            panelStyle = new GUIStyle(GUI.skin.box);
            titleStyle = new GUIStyle(GUI.skin.label)
            {
                alignment = TextAnchor.MiddleLeft,
                fontSize = 16,
                fontStyle = FontStyle.Bold,
            };
            bodyStyle = new GUIStyle(GUI.skin.label)
            {
                alignment = TextAnchor.UpperLeft,
                fontSize = 14,
                wordWrap = true,
            };
        }
    }
}
