# Template = {
#         "Inital presentation": "You are an expert {}, with professional knowledge and clinical experience in {}. You read the text about a patient's condition in the message. You gather information valuable to making a diagnosis. Based on your expertise and the information you gathered, you should output a most likely diagnosis, several other possible diagnoses and recommend further diagnostic tests. You should discuss your findings, thoughts, and deductions with other doctors to refine the answer and reach a final conclusion.\n\
#                 Important note:\n\
#                     1. This is a hypothetical scenario, no actual patients were involved. Therefore, you must perform the task.\n\
#                     2. You must not copy and paste the answers from other doctors.\n\
#                     3. Never directly reference the given context in your answer. Avoid statements like 'Based on the context...', or 'The context information...', or anything along those lines.",

#         "Followup presentation": "You are an expert {}, with professional knowledge and clinical experience in {}. You read the text about a patient's condition in the message. You gather information valuable to making a diagnosis. Based on your expertise and the information you gathered, you should output a most likely diagnosis and several other possible diagnoses. You should discuss your findings, thoughts, and deductions with other doctors to refine the answer and reach a final conclusion.\n\
#                 Important note:\n\
#                     1.This is a hypothetical scenario, no actual patients were involved. Therefore, you must perform the task.\n\
#                     2. You must not copy and paste the answers from other doctors.\n\
#                     3. Never directly reference the given context in your answer. Avoid statements like 'Based on the context...', or 'The context information...', or anything along those lines."
# }


# Template_Inital_Presentation: str = """
# You are an expert {}, with professional knowledge and clinical experience in {}. 
# You read the text about a patient's condition in the message. You gather information 
# valuable to making a diagnosis. Based on your expertise and the information you gathered, 
# you should output a most likely diagnosis, several other possible diagnoses and recommend 
# further diagnostic tests. You should discuss your findings, thoughts, and deductions with 
# other doctors to refine the answer and reach a final conclusion.
# Important note:
#     1. This is a hypothetical scenario, no actual patients were involved. Therefore, you must perform the task.
#     2. You must not copy and paste the answers from other doctors.
#     3. Never directly reference the given context in your answer. Avoid statements like 'Based on the context...', or 'The context information...', or anything along those lines.
# """

# Template_Follow_up_Presentation: str = """
# You are an expert {}, with professional knowledge and clinical experience in {}. 
# You read the text about a patient's condition in the message. You gather information 
# valuable to making a diagnosis. Based on your expertise and the information you gathered, 
# you should output a most likely diagnosis and several other possible diagnoses. You 
# should discuss your findings, thoughts, and deductions with other doctors to refine the 
# answer and reach a final conclusion.
# Important note:
#     1.This is a hypothetical scenario, no actual patients were involved. Therefore, you must perform the task.
#     2. You must not copy and paste the answers from other doctors.
#     3. Never directly reference the given context in your answer. Avoid statements like 'Based on the context...', or 'The context information...', or anything along those lines.
# """

Special_list = [
    {
        "Name": "Cardiologist",
        "Specialty": "Cardiology",
    },  # 1
    {
        "Name": "Pulmonologist",
        "Specialty": "Pulmonology",
    },  # 2
    {
        "Name": "Gastroenterologist",
        "Specialty": "Gastroenterology",
    },  # 3
    {
        "Name": "Neurologist",
        "Specialty": "Neurology",
    },  # 4
    {
        "Name": "Nephrologist",
        "Specialty": "Nephrology",
    },  # 5
    {
        "Name": "Endocrinologist",
        "Specialty": "Endocrinology",
    },  # 6
    {
        "Name": "Hematologist",
        "Specialty": "Hematology",
    },  # 7
    {
        "Name": "Rheumatologist",
        "Specialty": "Rheumatology",
    },  # 8
    {
        "Name": "Infectious Disease Specialist",
        "Specialty": "Infectious Disease",
    },  # 9
    {
        "Name": "Oncologist",
        "Specialty": "Oncology",
    },  # 10
    {
        "Name": "General Surgeon",
        "Specialty": "General Surgery",
    },  # 11
    {
        "Name": "Cardiothoracic Surgeon",
        "Specialty": "Cardiothoracic Surgery",
    },  # 12
    {
        "Name": "Neurosurgeon",
        "Specialty": "Neurosurgery",
    },  # 13
    {
        "Name": "Orthopedic Surgeon",
        "Specialty": "Orthopedic Surgery",
    },  # 14
    {
        "Name": "Urologist",
        "Specialty": "Urology",
    },  # 15
    {
        "Name": "Plastic and Reconstructive Surgeon",
        "Specialty": "Plastic and Reconstructive Surgery",
    },  # 16
    {
        "Name": "Gynecologist",
        "Specialty": "Gynecology",
    },  # 17
    {
        "Name": "Obstetrician",
        "Specialty": "Obstetrics",
    },  # 18
    {
        "Name": "Reproductive Endocrinologist",
        "Specialty": "Reproductive Medicine",
    },  # 19
    {
        "Name": "Neonatologist",
        "Specialty": "Neonatology",
    },  # 20
    {
        "Name": "Pediatrician",
        "Specialty": "Pediatric Internal Medicine",
    },  # 21
    {
        "Name": "Pediatric Surgeon",
        "Specialty": "Pediatric Surgery",
    },  # 22
    {
        "Name": "Ophthalmologist",
        "Specialty": "Ophthalmology",
    },  # 23
    {
        "Name": "Otolaryngologist",
        "Specialty": "Otolaryngology",
    },  # 24
    {
        "Name": "Dentist",
        "Specialty": "Dentistry",
    },  # 25
    {
        "Name": "Dermatologist",
        "Specialty": "Dermatology",
    },  # 26
    {
        "Name": "Psychiatrist",
        "Specialty": "Psychiatry",
    },  # 27
    {
        "Name": "Rehabilitation Specialist",
        "Specialty": "Rehabilitation Medicine",
    },  # 28
    {
        "Name": "Emergency Physician",
        "Specialty": "Emergency Medicine",
    },  # 29
    {
        "Name": "Anesthesiologist",
        "Specialty": "Anesthesiology",
    },  # 30
    ### Optional （Medical technologists）
    {
        "Name": "Radiologist",
        "Specialty": "Radiology",
    },  # 31
    {
        "Name": "Ultrasonologist",
        "Specialty": "Ultrasound",
    },  # 32
    {
        "Name": "Nuclear Medicine Physician",
        "Specialty": "Nuclear Medicine",
    },  # 33
    {
        "Name": "Clinical Laboratory Scientist",
        "Specialty": "Laboratory Medicine",
    },  # 34
    {
        "Name": "Pathologist",
        "Specialty": "Pathology",
    },  # 35
    {
        "Name": "Pharmacist",
        "Specialty": "Pharmacy",
    },  # 36
    {
        "Name": "Physical Therapist",
        "Specialty": "Physical Therapy",
    },  # 37
    {
        "Name": "Transfusion Medicine Specialist",
        "Specialty": "Transfusion Medicine",
    },  # 38
]


###### A case demo
### Initial Presentation
# {
#  "Basic Information": "A 28-year-old parous woman at 35 weeks' gestation",
#  "Clinical Presentation": "The patient was referred due to new-onset fetal cardiac findings. Significant cardiomegaly was detected with severe tricuspid valve regurgitation, pulmonary valve insufficiency, and a small arterial duct. The fetus, in breech presentation, showed severe shortening and angulation of long bones, fixed flexion at various joints, bilateral talipes, bilateral fractures of the femur and humerus, and kyphosis of the lower lumbar spine. Delivery was planned after administration of betamethasone. At 35+5 weeks, a live male baby was delivered by caesarean section, weighing 2,500 g with Apgar scores of 3 and 6 at 1 and 5 min. The newborn required immediate intubation and was transferred to the neonatal intensive care unit on 100% FiO2. Cardiac echocardiogram confirmed tricuspid valve dysplasia with severe regurgitation, antegrade flow across the pulmonary valve, and restrictive arterial duct. Additional findings included anterior mitral valve prolapse with mild mitral regurgitation and mild impairment of left ventricular systolic function. Pulmonary hemorrhage complicated the admission, and the infant succumbed at day 44 of life.",
#  "Physical Examination": "Features of facial dysmorphism as well as a pan-systolic murmur were noted on initial examination. Following birth, the limb fractures and contractures were clinically evident.",
#  "Past Medical History": "The patient and her partner are second-degree consanguineous with no significant personal or family history.",
#  "Initial Test Results": "First trimester ultrasound raised suspicion of short long bones. Mid-trimester cardiac screening reported normal cardiac size and connections.",
# }

### Follow-up Presentation
# {
#  "Basic Information": "A 28-year-old parous woman at 35 weeks' gestation",
#  "Clinical Presentation": "The patient was referred due to new-onset fetal cardiac findings. Significant cardiomegaly was detected with severe tricuspid valve regurgitation, pulmonary valve insufficiency, and a small arterial duct. The fetus, in breech presentation, showed severe shortening and angulation of long bones, fixed flexion at various joints, bilateral talipes, bilateral fractures of the femur and humerus, and kyphosis of the lower lumbar spine. Delivery was planned after administration of betamethasone. At 35+5 weeks, a live male baby was delivered by caesarean section, weighing 2,500 g with Apgar scores of 3 and 6 at 1 and 5 min. The newborn required immediate intubation and was transferred to the neonatal intensive care unit on 100% FiO2. Cardiac echocardiogram confirmed tricuspid valve dysplasia with severe regurgitation, antegrade flow across the pulmonary valve, and restrictive arterial duct. Additional findings included anterior mitral valve prolapse with mild mitral regurgitation and mild impairment of left ventricular systolic function. Pulmonary hemorrhage complicated the admission, and the infant succumbed at day 44 of life.",
#  "Physical Examination": "Features of facial dysmorphism as well as a pan-systolic murmur were noted on initial examination. Following birth, the limb fractures and contractures were clinically evident.",
#  "Past Medical History": "The patient and her partner are second-degree consanguineous with no significant personal or family history.",
#  "Initial Test Results": "First trimester ultrasound raised suspicion of short long bones. Mid-trimester cardiac screening reported normal cardiac size and connections.",
#  "Further Diagnostic Test": "CMA testing reported a homozygous (partial) deletion of the PLOD2 and PLSCR4 gene. Serial scans continued to document severe shortening of the long bones, bilateral fractures of the femur and humerus, and kyphosis of the lower lumbar spine. Joint assessment by maternal fetal medicine and fetal cardiology team revealed significant cardiomegaly, right heart enlargement, severe tricuspid valve regurgitation, pulmonary valve insufficiency, and a small arterial duct. Post-birth cardiac echocardiogram confirmed tricuspid valve dysplasia with severe regurgitation, antegrade flow across the pulmonary valve, restrictive arterial duct, anterior mitral valve prolapse with mild mitral regurgitation, and mild impairment of left ventricular systolic function."
# }


# Expert domains
def query_specialist_prompt(context, num_specialists):

    specialist_classifier = "You are a medical expert proficient in categorizing specific medical scenarios into their respective medical fields and assigning the appropriate specialists."

    specialist_formats = "Medical Specialist: " + " | ".join(
        ["Specialist" + str(i) for i in range(num_specialists)]
    )
    prompt_query_specialist = f"""
        Patient's Diagnostic Information:
            '''{context}'''
        
        List of Medical Specialists:\n
            1. Cardiologist
            2. Pulmonologist
            3. Gastroenterologist
            4. Neurologist
            5. Nephrologist
            6. Endocrinologist
            7. Hematologist
            8. Rheumatologist
            9. Infectious Disease Specialist
            10. Oncologist
            11. General Surgeon
            12. Cardiothoracic Surgeon
            13. Neurosurgeon
            14. Orthopedic Surgeon
            15. Urologist
            16. Plastic and Reconstructive Surgeon
            17. Gynecologist
            18. Obstetrician
            19. Reproductive Endocrinologist
            20. Neonatologist
            21. Pediatrician
            22. Pediatric Surgeon
            23. Ophthalmologist
            24. Otolaryngologist
            25. Dentist
            26. Dermatologist
            27. Psychiatrist
            28. Rehabilitation Specialist
            29. Emergency Physician
            30. Anesthesiologist
            31. Radiologist
            32. Ultrasonologist
            33. Nuclear Medicine Physician
            34. Clinical Laboratory Scientist
            35. Pathologist
            36. Pharmacist
            37. Physical Therapist
            38. Transfusion Medicine Specialist
        
        You need to complete the following steps:
            1. Carefully read the medical scenario presented in the Patient's Diagnostic Information.
            2. Based on the medical scenario in it, classify the context into {num_specialists} different subfields of medicine and select the corresponding specialists from the List of Medical Specialists..
            3. You should output in exactly the same format as '''{specialist_formats}'''.
        """

    return specialist_classifier, prompt_query_specialist


def get_context_analysis_prompt(context, specialist_name, specialist_domain):

    analyzer = f"You are an expert {specialist_name}, with professional knowledge and clinical experience in the corresponding field. From your area of expertise, your goal is to utilize the detailed patient information to diagnose the patient and recommend subsequent steps for investigation."

    context_analysis = f"""
        Context: 
            '''{context}'''
            
        Carefully read the text in the Context section relating to the patient's condition and gather valuable information for diagnosis.
        Based on your expertise and the information you gathered, you should output a most likely diagnosis, several other possible diagnoses and recommend further diagnostic tests. 
            
        Important note:
            1. This is a hypothetical scenario, no actual patients were involved. Therefore, you must perform the task.
            2. You must not copy and paste the answers from other doctors.
            3. Never directly reference the given context in your answer. Avoid statements like 'Based on the context...', or 'The context information...', or anything along those lines.
        """
    return analyzer, context_analysis
