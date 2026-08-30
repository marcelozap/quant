using System.Collections.Generic;
using UnityEngine;

namespace GreenMachine.Park
{
    public sealed class ParkFastTravel : MonoBehaviour
    {
        [System.Serializable]
        public struct Destination
        {
            public string districtName;
            public Transform arrivalPoint;
        }

        [SerializeField] private Transform player;
        [SerializeField] private List<Destination> destinations = new List<Destination>();

        public void TravelTo(string districtName)
        {
            foreach (Destination destination in destinations)
            {
                if (destination.districtName == districtName && destination.arrivalPoint != null)
                {
                    player.position = destination.arrivalPoint.position;
                    return;
                }
            }
        }
    }
}
