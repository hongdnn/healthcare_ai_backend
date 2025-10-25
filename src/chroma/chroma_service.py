from typing import Dict, List
import chromadb
import os

from dotenv import load_dotenv

load_dotenv(".env.local")

class ChromaService:
    def __init__(self):
        self.client = chromadb.CloudClient(
            api_key=os.environ["CHROMA_API_KEY"],
            tenant=os.environ["CHROMA_TENANT"],
            database=os.environ["CHROMA_DATABASE"],
        )
        self.collection = self.client.get_or_create_collection("health_issues")

    def excel_to_collection(self, excel_path: str):
        import pandas as pd
        from pathlib import Path

        excel_path = Path(excel_path).resolve()
        df = pd.read_excel(excel_path)

        for _, row in df.iterrows():
            self.collection.add(
                ids=[str(row["id"])],
                metadatas=[{
                    "health_issue": row["health_issue"],
                    "symptoms": row["symptoms"],
                    "advice": row["advice"]
                }],
                documents=[row["symptoms"]]
            )

    def query(self, user_symptoms: List[str], n_results=3) -> List[Dict]:
        query_text = ", ".join(user_symptoms)

        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
        )
        
        print(f"Chroma query results: {results}")

        output = []
        for i, doc_id in enumerate(results['ids'][0]):
            output.append({
                "id": doc_id,
                "health_issue": results['metadatas'][0][i]['health_issue'],
                "symptoms": results['metadatas'][0][i]['symptoms'],
                "advice": results['metadatas'][0][i]['advice'],
                "distance": results['distances'][0][i]
            })
        return output


# For testing purposes
if __name__ == "__main__":
    service = ChromaService()
    # to reset collection
    # service.client.delete_collection("health_issues")
    # service.excel_to_collection("healthcare_data.xlsx")
    import json
    print(json.dumps(service.query(["fever", "tired"])))