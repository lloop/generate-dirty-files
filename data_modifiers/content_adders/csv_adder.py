import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Union


class CSVAdder:
    """Generates and injects dynamic, randomized CSV content/sections

    to guarantee file variance across synthetic datasets.
    """

    def __init__(self):
        self.mock_departments = ["Sales", "Engineering", "HR", "Marketing", "Legal", "Operations"]
        self.mock_statuses = ["COMPLETED", "PENDING", "FAILED", "FLAGGED", "ARCHIVED"]
        self.mock_domains = ["example.com", "testcorp.org", "devmail.net", "datafirm.io"]

    def _generate_synthetic_row(self) -> str:
        """Generates a single randomized CSV row."""
        rec_id = f"REC-{random.randint(1000, 9999)}"
        timestamp = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d %H:%M:%S")
        user = f"user_{random.randint(100, 999)}@{random.choice(self.mock_domains)}"
        dept = random.choice(self.mock_departments)
        amount = round(random.uniform(10.5, 9999.99), 2)
        status = random.choice(self.mock_statuses)
        
        return f"{rec_id},{timestamp},{user},{dept},{amount},{status}"

    def generate_random_block(self, num_rows: int = 5, include_header: bool = False) -> List[str]:
        """Creates a standalone list of generated CSV rows."""
        rows = []
        if include_header:
            rows.append("record_id,timestamp,user_email,department,amount,status")
        
        for _ in range(num_rows):
            rows.append(self._generate_synthetic_row())
            
        return rows

    def inject_and_rearrange(self, file_path: Union[str, Path], num_new_rows: int = 5) -> None:
        """Reads existing CSV, appends synthetic data, splits the dataset into chunks,

        shuffles chunk ordering (preserving header), and writes back to disk.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Target file not found: {path}")

        lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

        if not lines:
            header = "record_id,timestamp,user_email,department,amount,status"
            body = self.generate_random_block(num_rows=num_new_rows)
            path.write_text("\n".join([header] + body) + "\n", encoding="utf-8")
            return

        header = lines[0]
        data_rows = lines[1:]

        # 1. Generate and append new dynamic rows
        new_rows = self.generate_random_block(num_rows=num_new_rows, include_header=False)
        data_rows.extend(new_rows)

        # 2. Break data into small sections/chunks for rearrangement
        chunk_size = max(1, len(data_rows) // 3)
        chunks = [data_rows[i:i + chunk_size] for i in range(0, len(data_rows), chunk_size)]

        # 3. Rearrange the sections randomly
        random.shuffle(chunks)

        # 4. Flatten rearranged sections back into a single list
        rearranged_body = [row for chunk in chunks for row in chunk]

        # 5. Write final reassembled CSV back to file
        final_content = "\n".join([header] + rearranged_body) + "\n"
        path.write_text(final_content, encoding="utf-8")


def modify_csv(file_path: Union[str, Path]) -> str:
    """Helper functional wrapper for integration into pipeline content modifiers."""
    adder = CSVAdder()
    adder.inject_and_rearrange(file_path)
    return "csv_rows_injected_and_rearranged"