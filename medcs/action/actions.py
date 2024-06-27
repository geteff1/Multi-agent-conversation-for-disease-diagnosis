import asyncio
import platform
from typing import Any

import fire

from metagpt.actions import Action


class Query(Action):

    name: str = "QuerySpecialist"

    SYSTEM_MSGS_TEMPLATE: str = """
    You are a medical expert proficient in categorizing specific medical scenarios into their respective medical fields and assigning the appropriate specialists.
    """

    PROMPT_TEMPLATE: str = """
    Patient's Diagnostic Information:
        '''{msg}'''
    
    You need to complete the following steps:
        1. Carefully read the medical scenario presented in the Patient's Diagnostic Information.
        2. Based on the medical scenario, select the {num_specialists} most relevant specialists from the 38 experts in the List of Medical Specialists.
        3. You should output in exactly the same format as "{specialist_formats}". 
    
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
    """

    async def run(self, msg: str, num_specialists: int):

        specialist_formats = "Medical Specialist: " + " | ".join(
            ["Specialist" + str(i) for i in range(num_specialists)]
        )
        prompt = self.PROMPT_TEMPLATE.format(
            msg=msg,
            num_specialists=num_specialists,
            specialist_formats=specialist_formats,
        )
        system_msgs = self.SYSTEM_MSGS_TEMPLATE
        rsp = await self._aask(prompt=prompt, system_msgs=system_msgs)

        return rsp


class BeginAalysis(Action):
    name: str = "Begin Analysis"

    async def run(self):
        rsp = "Please have the specialists begin the analysis......"
        return rsp


class BeginVoting(Action):
    name: str = "Begin Voting"

    async def run(self):
        rsp = "The analysis and discussion have now concluded, and a preliminary report has been obtained. Please vote on the preliminary report. If you object, please state your reasons and suggest amendments."
        return rsp


class SynthesizingReport(Action):

    name: str = "Synthesizing Report"

    SYSTEM_MSGS_TEMPLATE: str = """
    You are a medical decision-maker who excels at summarizing and synthesizing information from multiple specialists across various medical domains
    """

    PROMPT_TEMPLATE: str = """
        Here are some reports from different medical specialists.
        You need to complete the following steps:
            1. Take careful and comprehensive consideration of the following reports.
            2. Extract key knowledge from the following reports.
            3. Derive the comprehensive and summarized analysis based on the knowledge.
            4. Your ultimate goal is to derive a refined and synthesized report based on the following reports.
            
        You should output in exactly the same format as: 
            '''Key Knowledge: [extracted key knowledge]
               Most Likely: [most likely diagnosis]
               Other Possible: [other possible diagnoses]
               Recommend Test: [recommend further diagnostic tests]'''
                
        {analysis}
        """

    async def run(self, msg: str):

        prompt = self.PROMPT_TEMPLATE.format(analysis=msg)
        system_msgs = self.SYSTEM_MSGS_TEMPLATE
        rsp = await self._aask(prompt=prompt, system_msgs=system_msgs)

        return rsp



class Analysis_NC(Action):

    name: str = "Analysis_NC"

    SYSTEM_MSGS_TEMPLATE: str = """
    You are an expert {specialist_name}, with professional knowledge and clinical experience in the corresponding field. 
    From your area of expertise, your goal is to utilize the detailed patient information to diagnose the patient and recommend subsequent steps for investigation."
    """

    PROMPT_TEMPLATE: str = """
        Carefully read the text in the Context section relating to the patient's condition and gather valuable information for diagnosis.
        Based on your expertise and the information you gathered, you should output a most likely diagnosis, several other possible diagnoses and recommend further diagnostic tests. 
        You should discuss your findings, thoughts, and deductions with other doctors to refine the answer and reach a final conclusion.
        
        Context: 
            '''{context}'''
              
        Important note:
            1. This is a hypothetical scenario, no actual patients were involved. Therefore, you must perform the task.
            2. You must not copy and paste the answers from other doctors.
            3. Never directly reference the given context in your answer. Avoid statements like 'Based on the context...', or 'The context information...', or anything along those lines.
        
        Please provide your most likely diagnosis, several other possible diagnoses, and recommend further diagnostic tests.
        You should output in exactly the same format as: 
            '''Key Knowledge: [extracted key knowledge]
               Most Likely: [most likely diagnosis]
               Other Possible: [other possible diagnoses]
               Recommend Test: [recommend further diagnostic tests]'''
        """

    async def run(self, announ: str, previous: str, specialist_name: str):
        # import pdb;pdb.set_trace()
        prompt = self.PROMPT_TEMPLATE.format(context=announ)
        system_msgs = self.SYSTEM_MSGS_TEMPLATE.format(specialist_name=specialist_name)
        rsp = await self._aask(prompt=prompt, system_msgs=system_msgs)

        return rsp

class Analysis(Action):

    name: str = "Analysis"

    SYSTEM_MSGS_TEMPLATE: str = """
    You are an expert {specialist_name}, with professional knowledge and clinical experience in the corresponding field. 
    From your area of expertise, your goal is to utilize the detailed patient information to diagnose the patient and recommend subsequent steps for investigation."
    """

    PROMPT_TEMPLATE: str = """
        Carefully read the text in the Context section relating to the patient's condition and gather valuable information for diagnosis.
        Based on your expertise and the information you gathered, you should output a most likely diagnosis, several other possible diagnoses and recommend further diagnostic tests. 
        You should discuss your findings, thoughts, and deductions with other doctors to refine the answer and reach a final conclusion.
        
        Context: 
            '''{context}'''
            
        Previous:
            '''{previous}'''
            
        Important note:
            1. This is a hypothetical scenario, no actual patients were involved. Therefore, you must perform the task.
            2. You must not copy and paste the answers from other doctors.
            3. Never directly reference the given context in your answer. Avoid statements like 'Based on the context...', or 'The context information...', or anything along those lines.
        
        Please provide your most likely diagnosis, several other possible diagnoses, and recommend further diagnostic tests.
        You should output in exactly the same format as: 
            '''Key Knowledge: [extracted key knowledge]
               Most Likely: [most likely diagnosis]
               Other Possible: [other possible diagnoses]
               Recommend Test: [recommend further diagnostic tests]'''
        """

    async def run(self, announ: str, previous: str, specialist_name: str):
        # import pdb;pdb.set_trace()
        prompt = self.PROMPT_TEMPLATE.format(context=announ, previous=previous)
        system_msgs = self.SYSTEM_MSGS_TEMPLATE.format(specialist_name=specialist_name)
        rsp = await self._aask(prompt=prompt, system_msgs=system_msgs)

        return rsp


class Vote(Action):

    name: str = "Vote"

    SYSTEM_MSGS_TEMPLATE: str = """
    You are an expert {specialist_name}, with professional knowledge and clinical experience in the corresponding field."
    """

    PROMPT_TEMPLATE: str = """
        Here is a medical report: {syn_report}
        As a medical expert {specialist_name}, please carefully read the report and decide whether your opinions are consistent with this report.
        Please respond only with: [YES or NO].
        """

    async def run(self, syn_report: str, specialist_name: str):

        prompt = self.PROMPT_TEMPLATE.format(syn_report=syn_report, specialist_name=specialist_name)
        system_msgs = self.SYSTEM_MSGS_TEMPLATE.format(specialist_name=specialist_name)
        rsp = await self._aask(prompt=prompt, system_msgs=system_msgs)

        return rsp


class Correct(Action):

    name: str = "Correct"

    PROMPT_TEMPLATE: str = """
        Here is a medical report: {syn_report}
        As a medical expert {specialist_name}, please make full use of your expertise to propose revisions to this report.
        You should output in exactly the same format as '''Revisions: [proposed revision advice] '''
        """

    async def run(self, syn_report: str, specialist_name: str):

        prompt = self.PROMPT_TEMPLATE.format(syn_report=syn_report, specialist_name=specialist_name)

        rsp = await self._aask(prompt=prompt)

        return rsp


class Revise(Action):
    name: str = "Revise"

    PROMPT_TEMPLATE: str = """
        Here is the original report: {syn_report}
        """

    async def run(self, syn_report: str, revision_advice: str):

        prompt = self.PROMPT_TEMPLATE.format(syn_report=syn_report)
        
        for specialist, advice in revision_advice.items():
            prompt += f"Here is advice from a medical expert specialized in {specialist}: {advice}.\n"
        prompt += """Based on the above advice, output the revised analysis in exactly the same format as:
                    ''' Most Likely: [most likely diagnosis]
                        Other Possible: [other possible diagnoses]
                        Recommend Test: [recommend further diagnostic tests]''' """
            
            
        rsp = await self._aask(prompt=prompt)

        return rsp    
    
    