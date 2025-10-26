from pathlib import Path
from typing import Dict, List
import chromadb
import os

from dotenv import load_dotenv

load_dotenv(".env.local")
import pandas as pd

class ChromaService:
    """
    Alternative approach: Store each symptom as a separate document.
    This can provide even better individual symptom matching.
    """
    def __init__(self):
        # local chroma
        # self.client = chromadb.PersistentClient(path="./chroma_db")
        # cloud chroma
        self.client = chromadb.CloudClient(
            api_key=os.environ["CHROMA_API_KEY"],
            tenant=os.environ["CHROMA_TENANT"],
            database=os.environ["CHROMA_DATABASE"],
        )
        self.collection = self.client.get_or_create_collection("health_issues")

    def excel_to_collection(self, excel_path: str):
        excel_path = Path(excel_path).resolve()
        df = pd.read_excel(excel_path)

        for _, row in df.iterrows():
            symptoms_list = [s.strip().lower() for s in row["symptoms"].split(",") if s.strip()]
            
            # Store each symptom as a separate document with shared metadata
            for symptom_idx, symptom in enumerate(symptoms_list):
                doc_id = f"{row['id']}_{symptom_idx}"
                self.collection.add(
                    ids=[doc_id],
                    metadatas=[{
                        "health_issue_id": str(row["id"]),
                        "health_issue": row["health_issue"],
                        "all_symptoms": row["symptoms"], 
                        "advice": row["advice"],
                        "symptom": symptom
                    }],
                    documents=[symptom]
                )

    def query(self, user_symptoms: List[str], n_results=3) -> List[Dict]:
        """Query by aggregating scores across individual symptom matches (deduped per query symptom)."""
        all_matches = {}

        for symptom in user_symptoms:
            results = self.collection.query(
                query_texts=[symptom.lower()],
                n_results=100,
            )

            # Track which health issues were already matched for this query symptom
            seen_in_this_query = set()

            for i, doc_id in enumerate(results['ids'][0]):
                meta = results['metadatas'][0][i]
                health_issue_id = meta['health_issue_id']
                distance = results['distances'][0][i]

                # Skip if already matched this issue for the current query symptom
                if health_issue_id in seen_in_this_query:
                    continue
                seen_in_this_query.add(health_issue_id)

                if health_issue_id not in all_matches:
                    all_matches[health_issue_id] = {
                        "health_issue": meta['health_issue'],
                        "symptoms": meta['all_symptoms'],
                        "advice": meta['advice'],
                        "total_distance": 0.0,
                        "match_count": 0
                    }

                all_matches[health_issue_id]["total_distance"] += distance
                all_matches[health_issue_id]["match_count"] += 1

        # Compute averages
        output = []
        for health_id, data in all_matches.items():
            avg_distance = data["total_distance"] / data["match_count"]
            output.append({
                "id": health_id,
                "health_issue": data["health_issue"],
                "symptoms": data["symptoms"],
                "advice": data["advice"],
                "avg_distance": avg_distance,
                "match_count": data["match_count"]
            })

        # Sort by more matches (desc) and smaller avg distance (asc)
        output.sort(key=lambda x: (-x["match_count"], x["avg_distance"]))

        print(f"All matches: {all_matches}")
        return output[:n_results]


# For testing purposes
if __name__ == "__main__":
    service = ChromaService()
    # to reset collection
    # service.client.delete_collection("health_issues")
    service.excel_to_collection("healthcare_data.xlsx")
    print(service.query(["headache", "cough"], n_results=3))
