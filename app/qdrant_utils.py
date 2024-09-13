from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import numpy
from qdrant_client.http.models import ScrollRequest





# Initialize Qdrant client


def create_collection_if_not_exists(collection_name: str, vector_size: int):
    try:

        response = qdrant_client.get_collection(collection_name=collection_name)
        if response:
            print(f"Collection {collection_name} already exists.")
    except Exception as e:

        # print(f"Collection {collection_name} not found. Creating it now...")
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config={"size": vector_size, "distance": "Cosine"}  
        )
        # print(f"Collection {collection_name} created successfully.")


def insert_vectors_to_qdrant(vectors, user_id, filename, extracted_text, collection_name):
    try:
        points = []

        for i, vector in enumerate(vectors):
            if not isinstance(vector, (list, numpy.ndarray)):
                raise TypeError("Vector should be a list or numpy array.")
            
            if isinstance(vector, numpy.ndarray):
                vector = vector.tolist() 


            point = {
                "id": i, 
                "vector": vector, 
                "payload": {"user_id": user_id, "filename": filename, "text": extracted_text}
            }
            
            points.append(point)


        print("Prepared points for insertion:")
        for point in points:
            print(point)

        response = qdrant_client.upsert(
            collection_name=collection_name,
            points=points
        )


        print("Qdrant response:", response)

        print("Vectors inserted successfully.")
    except Exception as e:
        print(f"Error inserting vectors: {str(e)}")






# def check_collection_contents(collection_name):
#     try:
#         result = qdrant_client.search(
#             collection_name=collection_name,
#             query_vector=[0.0] * 384,  # Dummy vector to fetch results
#             limit=10
#         )
#         # print(f"Points in collection {collection_name}: {result}")
#     except Exception as e:
#         print(f"Error fetching collection contents: {str(e)}")





vectorizer_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def vectorize_question(question: str):
    question_vector = vectorizer_model.encode(question)
    if isinstance(question_vector, numpy.ndarray):
        assert question_vector.ndim == 1, "Vector must be 1-dimensional."
        assert len(question_vector) == 384, "Vector size mismatch."
    return question_vector




qdrant_client = QdrantClient(url="http://localhost:6333")  



def search_qdrant(question_vector, limit=3):
    try:
        # print(f"Searching Qdrant with vector: {question_vector} and limit: {limit}")
        search_result = qdrant_client.search(
            collection_name="Vectorized_file",
            query_vector=question_vector,
            limit=limit
        )
        # print("Search result:", search_result)
        
        answers = process_search_results(search_result)
        
        # if search_result:
        #     print(f"Found search results: {search_result}")
        # else:
        #     print("No search results found in Qdrant.")
        return search_result
    except Exception as e:
        print(f"Error during Qdrant search: {str(e)}")
        return None
    


def list_data_in_qdrant():
    try:
        all_data = qdrant_client.scroll(
            ScrollRequest(collection_name="Vectorized_file", limit=10)
        )
        # print(f"Data in Qdrant: {all_data}")
        return all_data
    except Exception as e:
        print(f"Error listing data in Qdrant: {str(e)}")
        return None





    

def process_search_results(results):
    try:
        for result in results:
            print("")
            if hasattr(result, 'payload'):
                print(result.payload['text']) 
            else:
                print("Invalid result format:", result)
    except AttributeError as e:
        print(f"Error: {str(e)}")



def optimize_collection(collection_name: str):
    try:
        qdrant_client.optimize(collection_name=collection_name)
        print(f"Optimization triggered for collection: {collection_name}")
    except Exception as e:
        print(f"Error during optimization: {str(e)}")



def update_collection_settings(collection_name: str, indexing_threshold: int):
    try:
        qdrant_client.update_collection(
            collection_name=collection_name,
            optimizer_config={
                "indexing_threshold": indexing_threshold
            }
        )
        print(f"Collection settings updated for {collection_name}")
    except Exception as e:
        print(f"Error updating collection settings: {str(e)}")





def retrieve_data_from_qdrant():
    try:

        response = qdrant_client.scroll(collection_name="Vectorized_file", limit=10) 

        # for result in response:
        #     print("Vector:", result.vector)
        #     print("Payload:", result.payload)
    except Exception as e:
        print(f"Error retrieving data: {e}")


retrieve_data_from_qdrant()