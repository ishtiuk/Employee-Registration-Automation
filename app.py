import os
import logging
import streamlit as st
from utils import read_yaml
from ocr_engine import extract_text
from create_database import create_table_if_not_exists
from preprocess import read_image, extract_id_card, save_image
from db_operations import insert_records, check_duplicacy, fetch_all_records
from postprocess import extract_information_genai, extract_information_regex
from face_verification import detect_and_extract_face, face_comparison, get_face_embeddings


logging_str = "[%(asctime)s: %(levelname)s: %(module)s]: %(message)s"
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(filename=os.path.join(log_dir, "employee_registration_logs.log"), level=logging.INFO, format=logging_str, filemode="a")

config_path = "config.yaml"
config = read_yaml(config_path)
artifacts = config['artifacts']
output_path = artifacts['INTERMIDEIATE_DIR']


with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def sidebar_section():
    st.sidebar.title("Employee Registration System")
    st.sidebar.markdown("Select a registration method below:")
    option = st.sidebar.selectbox("Choose a registration method", 
                              ("Select", "Manual Registration", "ID Card Registration", "View Registered Employees"),
                              label_visibility="collapsed")
    logging.info(f"Registration method selected: {option}")
    return option

# Manual registration form
def manual_registration_form():
    st.header("Manual Employee Registration")
    with st.form(key='manual_registration'):
        name = st.text_input("Full Name")
        job_position = st.text_input("Job Position")
        department = st.text_input("Department")
        emp_id = st.text_input("Employee ID")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        blood_group = st.text_input("Blood Group")
        dob = st.text_input("Date of Birth")
        submit_button = st.form_submit_button(label="Register")
        
        if submit_button:
            st.write("Registration successful!")
            # Handle registration logic here
            logging.info(f"Employee {emp_id} registered via manual form.")

# One-click signup with Employee ID card upload
def auto_registration_form():
    st.header("One-Click Employee Registration with ID Card")
    st.write("Upload your employee ID card image and a face image for automatic registration.")
    
    image_file = st.file_uploader("Upload Employee ID Card Image")
    face_image_file = st.file_uploader("Upload Face Image")

    col1, col2 = st.columns(2)
    
    with col1:
        if image_file is not None:
            st.image(
                image_file, 
                caption="ID Card Preview", 
                width=280, 
                use_column_width=False,
                output_format="auto"
            )
    
    with col2:
        if face_image_file is not None:
            st.image(
                face_image_file, 
                caption="Face Image Preview", 
                width=180, 
                use_column_width=False,
                output_format="auto"
            )

    if image_file is not None and face_image_file is not None:
        if image_file.getvalue() == face_image_file.getvalue():
            st.warning("You have uploaded the same image for both the ID card and face image. Please upload different images.")
            return

    if st.button("Register with ID"):
        with st.spinner("Processing your registration... Please wait while we verify your ID card and face image."):
            main_content(image_file, face_image_file)


def view_registered_employees():
    st.header("Registered Employees")
    employees = fetch_all_records()

    if employees is not None and not employees.empty:
        employees.columns = map(lambda x: x.title(), employees.columns)
        st.write("Here are the registered employees:")
        st.dataframe(employees)
    else:
        st.warning("No employees registered yet.")


def main_content(image_file, face_image_file):
    if image_file is not None:
        face_image = read_image(face_image_file, is_uploaded=True)
        logging.info("Face image loaded.")
        
        if face_image is not None:
            image = read_image(image_file, is_uploaded=True)
            logging.info("ID card image loaded.")
            image_roi, image_roi_path = extract_id_card(image)
            logging.info("ID card ROI extracted.")
            face_image_path2 = detect_and_extract_face(img=image_roi)
            face_image_path1 = save_image(face_image, "face_image.jpg", path=output_path)
            logging.info("Faces extracted and saved.")
            is_face_verified = face_comparison(image1_path=face_image_path1, image2_path=face_image_path2)
            logging.info(f"Face verification status: {'successful' if is_face_verified else 'failed'}.")

            if is_face_verified:
                extracted_text = extract_text(image_roi_path)
                try:
                    text_info = extract_information_genai(extracted_text)
                except Exception as e:
                    logging.error(f"Error using GenAI for information extraction: {e}")
                    text_info = extract_information_regex(extracted_text)
                    logging.info("Fallback to information extraction (Regex)")
                # print(get_face_embeddings(face_image_path1))
                    
                text_info['Embedding'] = get_face_embeddings(face_image_path1)              
                logging.info("Text extracted and information parsed from ID card.")
                
                if check_duplicacy(text_info):
                    st.warning(f"Employee already registered with ID: [{text_info['ID']}]")
                    logging.info(f"Duplicate record found for employee ID [{text_info['ID']}].")
                else:
                    insert_records(text_info)
                    st.success(f"Employee registered successfully! ID: [{text_info['ID']}]")
                    st.json(text_info)
                    logging.info(f"New employee record inserted: [{text_info['ID']}]")
            else:
                st.error("Face verification failed. Please try again.")
                logging.error("Face verification failed.")

        else:
            st.error("Face image not uploaded. Please upload a face image.")
            logging.error("No face image uploaded.")

    else:
        st.warning("Please upload an ID card image.")
        logging.warning("No ID card image uploaded.")

def main():
    option = sidebar_section()
    create_table_if_not_exists()

    if option == "Select":
        st.title("Welcome to the Employee Registration System")
        st.write("""
            **Welcome to our Employee Registration System!**  
            Here, you can easily register employees using either a manual form or an automatic process with ID card and face image upload.
            
            - **Manual Registration**: Enter employee details manually through a form.
            - **ID Card Registration**: Upload an employee ID card image and a face image for automatic registration with advanced verification.
            - **View Registered Employees**: View a list of all registered employees.

            Please choose the registration method from the sidebar to get started.
        """)
    elif option == "Manual Registration":
        manual_registration_form()
    elif option == "ID Card Registration":
        auto_registration_form()
    elif option == "View Registered Employees":
        view_registered_employees()


if __name__ == "__main__":
    main()
