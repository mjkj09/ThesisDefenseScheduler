import csv
from typing import List

from src.models import Role, Person, Defense


class CSVHandler:
    """Handles CSV import and export operations."""

    @staticmethod
    def export_persons(persons: List[Person], filepath: str) -> None:
        """Export persons to CSV file."""
        with open(filepath, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['name', 'email', 'roles'])
            writer.writeheader()

            for person in persons:
                roles_str = ';'.join(role.value for role in person.roles)
                writer.writerow({
                    'name': person.name,
                    'email': person.email,
                    'roles': roles_str
                })

    @staticmethod
    def import_persons(filepath: str) -> List[Person]:
        """Import persons from CSV file."""
        persons = []

        with open(filepath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                # Parse roles
                roles_str = row.get('roles', '')
                roles = set()
                if roles_str:
                    for role_str in roles_str.split(';'):
                        role_str = role_str.strip().lower()
                        for role in Role:
                            if role.value == role_str:
                                roles.add(role)
                                break

                # Create person
                try:
                    person = Person(
                        name=row['name'].strip(),
                        email=row['email'].strip(),
                        roles=roles if roles else {Role.SUPERVISOR}  # Default role
                    )
                    persons.append(person)
                except (KeyError, ValueError) as e:
                    print(f"Error importing person from row {row}: {e}")
                    continue

        return persons

    @staticmethod
    def export_defenses(defenses: List[Defense], filepath: str) -> None:
        """Export defenses to CSV file."""
        with open(filepath, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=[
                'student_name', 'thesis_title', 'supervisor_email', 'reviewer_email'
            ])
            writer.writeheader()

            for defense in defenses:
                writer.writerow({
                    'student_name': defense.student_name,
                    'thesis_title': defense.thesis_title,
                    'supervisor_email': defense.supervisor.email,
                    'reviewer_email': defense.reviewer.email
                })

    @staticmethod
    def import_defenses(filepath: str, persons: List[Person]) -> List[Defense]:
        """Import defenses from CSV file. Requires existing persons list."""
        defenses = []

        # Create email to person mapping
        person_map = {p.email: p for p in persons}

        with open(filepath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                try:
                    supervisor_email = row['supervisor_email'].strip()
                    reviewer_email = row['reviewer_email'].strip()

                    # Find supervisor and reviewer
                    supervisor = person_map.get(supervisor_email)
                    reviewer = person_map.get(reviewer_email)

                    if not supervisor:
                        print(f"Supervisor with email {supervisor_email} not found")
                        continue
                    if not reviewer:
                        print(f"Reviewer with email {reviewer_email} not found")
                        continue

                    # Create defense
                    defense = Defense(
                        student_name=row['student_name'].strip(),
                        thesis_title=row['thesis_title'].strip(),
                        supervisor=supervisor,
                        reviewer=reviewer
                    )
                    defenses.append(defense)

                except (KeyError, ValueError) as e:
                    print(f"Error importing defense from row {row}: {e}")
                    continue

        return defenses

    @staticmethod
    def create_sample_persons_csv(filepath: str) -> None:
        """Create a sample persons CSV file for testing."""
        sample_data = [
            {'name': 'Dr. John Smith', 'email': 'john.smith@university.edu',
             'roles': 'supervisor;reviewer;chairman'},
            {'name': 'Prof. Jane Doe', 'email': 'jane.doe@university.edu',
             'roles': 'supervisor;reviewer;chairman'},
            {'name': 'Dr. Bob Johnson', 'email': 'bob.johnson@university.edu',
             'roles': 'supervisor;reviewer'},
            {'name': 'Dr. Alice Williams', 'email': 'alice.williams@university.edu',
             'roles': 'reviewer;chairman'},
            {'name': 'Prof. Charlie Brown', 'email': 'charlie.brown@university.edu',
             'roles': 'supervisor;reviewer;chairman'},
        ]

        with open(filepath, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['name', 'email', 'roles'])
            writer.writeheader()
            writer.writerows(sample_data)

    @staticmethod
    def create_sample_defenses_csv(filepath: str) -> None:
        """Create a sample defenses CSV file for testing."""
        sample_data = [
            {'student_name': 'Anna Kowalska',
             'thesis_title': 'Machine Learning in Medical Diagnosis',
             'supervisor_email': 'john.smith@university.edu',
             'reviewer_email': 'jane.doe@university.edu'},
            {'student_name': 'Piotr Nowak',
             'thesis_title': 'Blockchain Technology in Supply Chain Management',
             'supervisor_email': 'jane.doe@university.edu',
             'reviewer_email': 'bob.johnson@university.edu'},
            {'student_name': 'Maria Wiśniewska',
             'thesis_title': 'AI-Powered Natural Language Processing',
             'supervisor_email': 'charlie.brown@university.edu',
             'reviewer_email': 'alice.williams@university.edu'},
            {'student_name': 'Tomasz Lewandowski',
             'thesis_title': 'Quantum Computing Applications',
             'supervisor_email': 'bob.johnson@university.edu',
             'reviewer_email': 'john.smith@university.edu'},
        ]

        with open(filepath, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=[
                'student_name', 'thesis_title', 'supervisor_email', 'reviewer_email'
            ])
            writer.writeheader()
            writer.writerows(sample_data)