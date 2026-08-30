using System;
using UnityEngine;

namespace GreenMachine.Park
{
    public sealed class XIVInteractable : MonoBehaviour
    {
        [SerializeField] private string interactionName = "Inspect";
        [TextArea(2, 4)] [SerializeField] private string message = "A small detail worth noticing.";
        [SerializeField] private bool singleUse = true;
        [SerializeField] private Renderer visual;
        [SerializeField] private Color interactedColor = new Color(0.6f, 0.82f, 0.72f);

        private Material visualMaterial;
        private bool interacted;

        public event Action<string> Interacted;
        public string InteractionName => interactionName;
        public string Message => message;
        public bool CanInteract => !singleUse || !interacted;
        public Vector3 FocusPosition => transform.position;

        private void Awake()
        {
            if (visual == null) visual = GetComponentInChildren<Renderer>();
            if (visual != null) visualMaterial = visual.material;
        }

        public bool TryInteract()
        {
            if (!CanInteract) return false;

            interacted = true;
            if (visualMaterial != null) visualMaterial.color = interactedColor;
            Interacted?.Invoke(interactionName);
            return true;
        }
    }
}
