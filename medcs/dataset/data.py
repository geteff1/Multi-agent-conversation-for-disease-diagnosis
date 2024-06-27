import json
import os.path as osp


class MedDataset:

    dataset_dir = "datasets"  # the directory where the dataset is stored

    def __init__(self, dataname: str="rare_disease_cases_150"):
        dataname = f"{dataname}.json"
        self.data_path = osp.join(self.dataset_dir, dataname)
        self.cases = None
        self.load()


    def __len__(self):
        return len(self.cases)

    def load(self):
        with open(self.data_path, "r") as file:
            data = json.load(file)
            self.cases = data["Cases"]

    def __getitem__(self, idx: int):
        case = self.cases[idx]
        disease_type = case["Type"]
        disease_name = case["Final Name"]
        disease_crl = case["Case URL"]
        disease_initial_presentation = case["Initial Presentation"]
        disease_follow_up_presentation = case["Follow-up Presentation"]
        
        return disease_type, disease_name, disease_crl, disease_initial_presentation, disease_follow_up_presentation