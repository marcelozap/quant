using UnityEngine;

namespace GreenMachine.Park
{
    public sealed class RoscoInterestPoint : MonoBehaviour
    {
        [SerializeField] private string pointName = "Point of interest";
        [SerializeField] [Min(0.5f)] private float pauseSeconds = 2.5f;
        [SerializeField] private bool repeatable;
        [SerializeField] private Renderer visual;
        [SerializeField] private Color discoveredColor = new Color(1f, 0.78f, 0.28f);
        [SerializeField] [Min(0f)] private float pulseSpeed = 2.2f;
        [SerializeField] [Range(0f, 0.3f)] private float pulseAmount = 0.08f;

        private Vector3 baseScale;
        private Material visualMaterial;
        private bool discovered;

        public string PointName => pointName;
        public float PauseSeconds => pauseSeconds;
        public bool Repeatable => repeatable;
        public bool IsDiscovered => discovered;

        private void Awake()
        {
            if (visual == null) visual = GetComponentInChildren<Renderer>();
            baseScale = transform.localScale;
            if (visual != null) visualMaterial = visual.material;
        }

        private void Update()
        {
            if (pulseSpeed <= 0f || pulseAmount <= 0f) return;
            float pulse = 1f + Mathf.Sin(Time.time * pulseSpeed) * pulseAmount;
            transform.localScale = baseScale * pulse;
        }

        public void MarkDiscovered()
        {
            if (discovered) return;
            discovered = true;
            if (visualMaterial != null) visualMaterial.color = discoveredColor;
        }
    }
}
