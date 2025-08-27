from models.tools import DateModel, DateTimeModel, IdentificationNumberModel
from langchain_core.tools import tool
import pandas as pd
from datetime import datetime
import logging, os, requests
from service.hospital_search import locator
from typing import Dict, Any, Optional, List
# from tools.vectorstore import get_retriever
from langchain_chroma.vectorstores import chromadb
import os
import json

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

def convert_datetime_format(dt_str):
    # Parse the input datetime string
    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")

    # Format the output as 'DD-MM-YYYY H.M' (removing leading zero from hour only)
    return dt.strftime("%d-%m-%Y %#H.%M")

# dataset_retriver = get_retriever()

# @tool
# def vector_tool(query: str) -> str:
#     """Use this tool to answer medical questions."""
#     logger.info(f"🔍 Calling vector_tool with query: {query}")  
#     # results = dataset_retriver.get_relevant_documents(query)
#     results = dataset_retriver.invoke(query)
#     string_results = "\n".join([doc.page_content for doc in results])
#     logger.info(f"✅ vector_tool results: {string_results}") 
#     return string_results


chroma_host=os.environ.get("CHROMADB_HOST")
chroma_port=os.environ.get("CHROMADB_PORT")

@tool  
def vector_tool(query: str) -> str:
    """Direct ChromaDB server approach - potentially faster"""
    logger.info(f"🔍 Direct ChromaDB query: {query}")
    
    try:
        client = chromadb.HttpClient(host=chroma_host, port=chroma_port)
        # collections = client.list_collections()
        collection = client.get_collection(name="langchain")
        
        if not collection:
            return "No collections available"
            
        # collection = collections[0]  # Your langchain collection
        
        # Direct query to ChromaDB
        results = collection.query(
            query_texts=[query],
            n_results=4,  # Adjust as needed
            # include=["documents", "metadatas"]
        )
        
        if results['documents'] and results['documents'][0]:
            string_results = "\n".join(results['documents'][0])
            logger.info(f"✅ Direct query found {len(results['documents'][0])} results")
            return string_results
        else:
            return "No relevant documents found"
            
    except Exception as e:
        logger.error(f"❌ Direct query error: {e}")
        return f"Error: {e}"

@tool
def check_availability_by_doctor(
        query_date: str,
        doctor_name: str,
        hospital_name: str,
        user_id: str
    ) -> dict:
    """
    Checking the database if we have availability for the specific doctor.
    The parameters should be mentioned by the user in the query
    """
    try:

        base_url = "http://localhost:7001"
        endpoint = f"/availability"
        api_url = base_url + endpoint

        params = {
            'query_date': query_date,
            'doctor_name': doctor_name,
            'hospital_name': hospital_name,
            'current_user': user_id
        }
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()
        available_slots = [
            item['date_slot'].split(' ')[1] for item in data.get("data", [])
        ]
        if not available_slots:
            output = "No availability in the entire day"
        else:
            output = f'This availability for {query_date}\n'
            output += "Available slots: " + ', '.join(available_slots)
        return {'message': data.get('message'), 'data': output}
    except requests.exceptions.RequestException as e:
        return f"Error checking availability: {str(e)}"


@tool
def get_doctor_info_by_hospital_name(
        hospital_name: str) -> List[Dict[str, Any]]:
    """
    Get information about doctors at a specific hospital.

    Args:
        name (str): The name of the hospital to search for doctors.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing doctor information.
    """
    try:
        # Format the API URL
        base_url = "http://127.0.0.1:7001"
        endpoint = f"/doctor"
        api_url = base_url + endpoint
        params = {'hospital_name': hospital_name.lower()}
        # Make GET request to the API
        response = requests.get(api_url, params=params)
        # Check if request was successful
        response.raise_for_status()
        # Parse the response
        data = response.json()
        return data

    except requests.exceptions.RequestException as e:
        return f"Error checking availability: {str(e)}"


@tool
def check_availability_by_specialization(
    # desired_date: DateModel,
    desired_date: str,
    specialization: str
    ):
    """
    Checking the database if we have availability for the specific specialization.
    The parameters should be mentioned by the user in the query
    """
    # Dummy data
    # df = pd.read_csv(f"availability.csv")
    csv_path = os.path.join(os.path.dirname(__file__), "availability.csv")
    df = pd.read_csv(csv_path)

    df["date_slot_time"] = df["date_slot"].apply(lambda input: input.split(" ")[-1])
    rows = (
        df[
            (df["date_slot"].apply(lambda input: input.split(" ")[0])== desired_date.date) &
            (df["specialization"] == specialization) &
            (df["is_available"] == True)
        ]
        .groupby(["specialization", "doctor_name"])["date_slot_time"]
        .apply(list)
        .reset_index(name="available_slots")
    )

    if len(rows) == 0:
        output = "No availability in the entire day"
    else:

        def convert_to_am_pm(time_str):
            # Split the time string into hours and minutes
            time_str = str(time_str)
            hours, minutes = map(int, time_str.split("."))

            # Determine AM or PM
            period = "AM" if hours < 12 else "PM"

            # Convert hours to 12-hour format
            hours = hours % 12 or 12

            # Format the output
            return f"{hours}:{minutes:02d} {period}"

        output = f"This availability for {desired_date.date}\n"
        for row in rows.values:
            output += (
                row[1]
                + ". Available slots: \n"
                + ", \n".join([convert_to_am_pm(value) for value in row[2]])
                + "\n"
            )
    return output


@tool
def cancel_appointment(
    query_date: str, 
    doctor_name: str, 
    hospital_name: str, 
    user_id: str):
    """
    Canceling an appointment.
    The parameters MUST be mentioned by the user in the query.
    
    [Args]: patient_to_attend(str) is acting like id_number
    """
    try:
        # Format the API URL
        api_url = "http://127.0.0.1:7001/cancel"
        params = {
            'query_date': query_date,
            'doctor_name': doctor_name.lower(),
            'hospital_name': hospital_name.lower(),
            'patient_to_attend': user_id
        }
        # Make GET request to the API
        response = requests.post(api_url, params=params)
        # Check if request was successful
        response.raise_for_status()
        # Parse the response
        data = response.json()
        return data

    except requests.exceptions.RequestException as e:
        return f"Error checking availability: {str(e)}"


@tool
def set_appointment(
    query_date: str,
    doctor_name: str,
    hospital_name: str,
    user_id: str
) -> str:
    """Book appointment with selected doctor."""

    try:
        api_url = "http://127.0.0.1:7001/booking"
        params = {
            'query_date': query_date,
            'doctor_name': doctor_name.lower(),
            'hospital_name': hospital_name.lower(),
            'patient_to_attend': user_id
        }

        response = requests.post(api_url, params=params)
        response.raise_for_status()

        data = response.json()
        return f"✅ Appointment booked: {data}"

    except requests.exceptions.RequestException as e:
        logger.error(f"[ERROR] Failed to book appointment: {e}")
        return f"❌ Error booking appointment: {str(e)}"


@tool
def reschedule_appointment(
    old_date: DateTimeModel,
    new_date: DateTimeModel,
    id_number: IdentificationNumberModel,
    doctor_name: str,
):
    """
    Rescheduling an appointment.
    The parameters MUST be mentioned by the user in the query.
    """
    df = pd.read_csv(f"availability.csv")
    available_for_desired_date = df[
        (df["date_slot"] == convert_datetime_format(new_date.date))
        & (df["is_available"] == True)
        & (df["doctor_name"] == doctor_name)
    ]
    if len(available_for_desired_date) == 0:
        return "Not available slots in the desired period"
    else:
        cancel_appointment.invoke(
            {"date": old_date, "id_number": id_number, "doctor_name": doctor_name}
        )
        set_appointment.invoke(
            {
                "desired_date": new_date,
                "id_number": id_number,
                "doctor_name": doctor_name,
            }
        )
        return "Succesfully rescheduled for the desired time"


    # Args:
    #     zipcode (Optional[str]): The ZIP code to search for hospitals. If not provided,
    #                             uses current location.

@tool
def find_nearby_hospital() -> List[Dict[str, Any]]:
    """
    Find and return information about nearby hospitals based on current location.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing hospital information including:
            - hospital_info:
                - name: Name of the hospital
                - location: Dictionary containing latitude and longitude
                - distance: Distance from current location in meters
    """
    try:
        print("HospitalLocator initialized successfully")  # Debug log
        # result = (
        #     locator.search_hospitals(zipcode)
        #     if zipcode
        #     else locator.handle_hospital_query()
        # )
        result = (
            locator.search_hospitals_based_on_zipcode()
        )
        print(f"Result from search_hospitals: {result}")  # Debug log
        if not result:
            return [{"error": "No hospitals found in the specified area"}]
        hospital_lines = [
            f"{i+1}. {h['hospital_info']['name']} ({h['hospital_info']['distance']/1000:.1f} km)"
            for i, h in enumerate(result)
        ]
        response = "Here are the nearby hospitals:\n" + "\n".join(hospital_lines)
        return result
    except Exception as e:
        print(f"Error in find_nearby_hospital: {str(e)}")  # Debug log
        raise ValueError(f"Failed to locate nearby hospitals: {str(e)}")
