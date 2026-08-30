using UnityEngine;

namespace GreenMachine.Park
{
    public sealed class DistrictPortal : MonoBehaviour
    {
        [SerializeField] private string districtName;
        [SerializeField] private Transform destination;

        private void OnTriggerEnter(Collider other)
        {
            if (!other.CompareTag("Player") || destination == null) return;
            other.transform.position = destination.position;
            Debug.Log($"Green Machine: entered {districtName}");
        }
    }
}
