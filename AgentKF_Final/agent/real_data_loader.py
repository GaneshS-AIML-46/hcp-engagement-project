
# ============================================================
# AgentKF - REAL DATA LOADER
# ============================================================

from pathlib import Path
import pandas as pd


class RealDataLoader:

    def __init__(self, input_directory):

        self.input_directory = Path(
            input_directory
        )


    def load_csv(self, filename):

        path = (
            self.input_directory
            / filename
        )

        if not path.exists():

            raise FileNotFoundError(
                f"File not found: {path}"
            )

        return pd.read_csv(path)


    def list_files(self):

        return [
            file.name
            for file
            in self.input_directory.glob("*.csv")
        ]


    def load_available_files(self):

        datasets = {}

        for file in self.input_directory.glob(
            "*.csv"
        ):

            try:

                datasets[file.name] = (
                    pd.read_csv(file)
                )

            except Exception as error:

                print(
                    f"Could not load {file.name}: "
                    f"{error}"
                )

        return datasets
