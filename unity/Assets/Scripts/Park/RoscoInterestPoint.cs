using UnityEngine;

namespace GreenMachine.Park
{
    public sealed class RoscoInterestPoint : MonoBehaviour
    {
        [SerializeField] private string pointName = "Point of interest";
        [SerializeField] [Min(0.5f)] private float pauseSeconds = 2.5f;
        [SerializeField] private bool repeatable;

        public string PointName => pointName;
        public float PauseSeconds => pauseSeconds;
        public bool Repeatable => repeatable;
    }
}
