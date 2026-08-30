using System;
using System.Collections.Generic;
using UnityEngine;

namespace GreenMachine.Park
{
    /// <summary>Builds a symbol's history path from descriptive closed-trade data only.</summary>
    public sealed class TradeStonePath : MonoBehaviour
    {
        [Serializable]
        public struct ClosedTrade
        {
            public string closedDate;
            public float gainLoss;
            public float returnPercent;
        }

        [SerializeField] private Transform pathRoot;
        [SerializeField] private Material positiveStone;
        [SerializeField] private Material negativeStone;
        [SerializeField] private Material neutralStone;
        [SerializeField] private float spacing = 1.15f;
        [SerializeField] private float curveWidth = 1.2f;

        private readonly List<GameObject> spawnedStones = new List<GameObject>();

        public void Populate(IReadOnlyList<ClosedTrade> trades)
        {
            Clear();
            if (trades == null || pathRoot == null) return;

            for (int index = 0; index < trades.Count; index++)
            {
                ClosedTrade trade = trades[index];
                GameObject stone = GameObject.CreatePrimitive(PrimitiveType.Cube);
                stone.name = $"Trade Stone {index + 1} - {trade.closedDate}";
                stone.transform.SetParent(pathRoot, false);
                float side = (index % 2 == 0 ? -1f : 1f) * curveWidth;
                stone.transform.localPosition = new Vector3(side, 0.1f, index * spacing);
                stone.transform.localScale = new Vector3(0.9f, 0.18f, 0.72f);
                stone.transform.localRotation = Quaternion.Euler(0f, side * 10f, 0f);
                stone.GetComponent<Renderer>().sharedMaterial = MaterialFor(trade.gainLoss);
                spawnedStones.Add(stone);
            }
        }

        public void Clear()
        {
            foreach (GameObject stone in spawnedStones)
            {
                if (stone != null) Destroy(stone);
            }
            spawnedStones.Clear();
        }

        private Material MaterialFor(float gainLoss)
        {
            // Both outcomes use polished materials: this path records history, never grades it.
            if (gainLoss > 0f) return positiveStone != null ? positiveStone : neutralStone;
            if (gainLoss < 0f) return negativeStone != null ? negativeStone : neutralStone;
            return neutralStone;
        }
    }
}
