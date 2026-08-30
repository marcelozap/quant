using System.Collections.Generic;
using UnityEngine;
using UnityEngine.InputSystem;

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
        [SerializeField] private RoscoCompanion rosco;
        [SerializeField] private List<Destination> destinations = new List<Destination>();
        [SerializeField] private string whistleDestination = "Green Gate";

        private void Update()
        {
            if (Keyboard.current != null && Keyboard.current.tKey.wasPressedThisFrame)
            {
                WhistleForRosco();
            }
        }

        public void WhistleForRosco()
        {
            // Fast travel is a convenience gesture, not a reward tied to market outcomes.
            if (rosco != null) rosco.Recall();
            TravelTo(whistleDestination);
        }

        public void TravelTo(string districtName)
        {
            foreach (Destination destination in destinations)
            {
                if (destination.districtName == districtName && destination.arrivalPoint != null)
                {
                    player.position = destination.arrivalPoint.position;
                    if (rosco != null) rosco.RejoinPlayer();
                    return;
                }
            }
        }
    }
}
