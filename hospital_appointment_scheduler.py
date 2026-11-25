"""
Hospital Appointment Scheduler  (PS No. 81)
-------------------------------------------
A console program for a clinic receptionist to Book, View, Reschedule
and Cancel patient appointments.

Concepts used : Dictionaries, Datetime, Functions, CRUD
Language      : Python 3

Rules
  * Appointments are stored in a dictionary:
        { "A101": {"patient": ..., "doctor": ..., "date": ..., "time": ...} }
  * Appointment IDs are auto-generated (A101, A102, ...).
  * Slots are 30 minutes long, from 09:00 to 16:30.
  * Date format DD-MM-YYYY, time format HH:MM (validated with datetime).
  * A doctor cannot have two appointments at the same date and time.
  * Doctors available: Dr. Mehta, Dr. Rao.
"""

from datetime import datetime, time

# ----------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------
DOCTORS = ("Dr. Mehta", "Dr. Rao")
DATE_FORMAT = "%d-%m-%Y"
TIME_FORMAT = "%H:%M"
SLOT_START = time(9, 0)      # first slot
SLOT_END = time(16, 30)      # last slot (starts at 16:30)
SLOT_MINUTES = 30
FIRST_ID_NUMBER = 101        # first generated ID is A101


# ----------------------------------------------------------------------
# Validation helpers
# ----------------------------------------------------------------------
class Validator:
    """Static helpers that check and normalise user input."""

    @staticmethod
    def validate_name(text):
        """Return the cleaned patient name, or None if it is empty."""
        name = " ".join(text.split())
        return name if name else None

    @staticmethod
    def validate_doctor(text):
        """Return the official doctor name (e.g. 'Dr. Mehta') or None."""
        key = text.strip().lower().replace("dr.", "").replace("dr ", "").strip()
        for doctor in DOCTORS:
            if doctor.lower().replace("dr. ", "") == key:
                return doctor
        return None

    @staticmethod
    def validate_date(text):
        """Return the date as 'DD-MM-YYYY' if valid (real calendar date), else None."""
        text = text.strip()
        try:
            parsed = datetime.strptime(text, DATE_FORMAT)
        except ValueError:
            return None
        # strptime accepts '5-1-2026'; insist on the exact DD-MM-YYYY form.
        return text if parsed.strftime(DATE_FORMAT) == text else None

    @staticmethod
    def validate_time(text):
        """Return the time as 'HH:MM' if it is a valid 30-minute slot
        between 09:00 and 16:30, else None."""
        text = text.strip()
        try:
            parsed = datetime.strptime(text, TIME_FORMAT).time()
        except ValueError:
            return None
        if parsed.strftime(TIME_FORMAT) != text:
            return None
        if parsed.minute % SLOT_MINUTES != 0:
            return None
        if not (SLOT_START <= parsed <= SLOT_END):
            return None
        return text


# ----------------------------------------------------------------------
# Scheduler (CRUD operations on the dictionary)
# ----------------------------------------------------------------------
class AppointmentScheduler:
    """Holds the appointment dictionary and performs CRUD operations.
    Every operation returns (success: bool, message: str)."""

    MSG_BAD_DATE = "Invalid date. Please enter the date as DD-MM-YYYY."
    MSG_BAD_TIME = ("Invalid time. Please enter a 30-minute slot between "
                    "09:00 and 16:30 as HH:MM.")
    MSG_BAD_DOCTOR = "Invalid doctor. Available doctors: " + ", ".join(DOCTORS) + "."
    MSG_BAD_NAME = "Patient name cannot be empty."

    def __init__(self):
        self.appointments = {}               # ID -> appointment record (dict)
        self._last_number = FIRST_ID_NUMBER - 1

    # ---- helpers ------------------------------------------------------
    def _generate_id(self):
        """Create the next auto-generated appointment ID (A101, A102, ...)."""
        self._last_number += 1
        return f"A{self._last_number}"

    def _is_slot_taken(self, doctor, date, time_text, ignore_id=None):
        """True if the doctor already has an appointment at date + time."""
        for appt_id, record in self.appointments.items():
            if appt_id == ignore_id:
                continue
            if (record["doctor"] == doctor and record["date"] == date
                    and record["time"] == time_text):
                return True
        return False

    @staticmethod
    def _format(appt_id, record):
        return (f"{appt_id} | {record['patient']} | {record['doctor']} | "
                f"{record['date']} {record['time']}")

    @staticmethod
    def _sort_key(item):
        """Sort by actual date and time (not by text)."""
        record = item[1]
        return datetime.strptime(f"{record['date']} {record['time']}",
                                 f"{DATE_FORMAT} {TIME_FORMAT}")

    # ---- CREATE -------------------------------------------------------
    def book(self, patient, doctor, date, time_text):
        patient = Validator.validate_name(patient)
        if patient is None:
            return False, self.MSG_BAD_NAME
        doctor = Validator.validate_doctor(doctor)
        if doctor is None:
            return False, self.MSG_BAD_DOCTOR
        date = Validator.validate_date(date)
        if date is None:
            return False, self.MSG_BAD_DATE
        time_text = Validator.validate_time(time_text)
        if time_text is None:
            return False, self.MSG_BAD_TIME
        if self._is_slot_taken(doctor, date, time_text):
            return False, (f"Slot unavailable: {doctor} already has an "
                           f"appointment on {date} at {time_text}.")

        appt_id = self._generate_id()
        self.appointments[appt_id] = {
            "patient": patient, "doctor": doctor,
            "date": date, "time": time_text,
        }
        return True, "Appointment booked. ID: " + self._format(
            appt_id, self.appointments[appt_id])

    # ---- READ ---------------------------------------------------------
    def view_all(self):
        if not self.appointments:
            return True, "No appointments scheduled.\nTotal appointments: 0"
        lines = [self._format(appt_id, record) for appt_id, record
                 in sorted(self.appointments.items(), key=self._sort_key)]
        lines.append(f"Total appointments: {len(self.appointments)}")
        return True, "\n".join(lines)

    # ---- UPDATE -------------------------------------------------------
    def reschedule(self, appt_id, new_date, new_time):
        appt_id = appt_id.strip().upper()
        if appt_id not in self.appointments:
            return False, f"Appointment ID {appt_id} not found."
        new_date = Validator.validate_date(new_date)
        if new_date is None:
            return False, self.MSG_BAD_DATE
        new_time = Validator.validate_time(new_time)
        if new_time is None:
            return False, self.MSG_BAD_TIME

        record = self.appointments[appt_id]
        if self._is_slot_taken(record["doctor"], new_date, new_time,
                               ignore_id=appt_id):
            return False, (f"Slot unavailable: {record['doctor']} already has "
                           f"an appointment on {new_date} at {new_time}.")
        record["date"], record["time"] = new_date, new_time
        return True, f"Appointment {appt_id} rescheduled to {new_date} {new_time}."

    # ---- DELETE -------------------------------------------------------
    def cancel(self, appt_id):
        appt_id = appt_id.strip().upper()
        if appt_id not in self.appointments:
            return False, f"Appointment ID {appt_id} not found."
        del self.appointments[appt_id]
        return True, f"Appointment {appt_id} cancelled."


# ----------------------------------------------------------------------
# Console menu
# ----------------------------------------------------------------------
MENU = """
===== HOSPITAL APPOINTMENT SCHEDULER =====
1. Book appointment
2. View all appointments
3. Reschedule appointment
4. Cancel appointment
5. Exit"""


def book_menu(scheduler):
    patient = input("Patient name: ")
    doctor = input("Doctor (Dr. Mehta / Dr. Rao): ")
    date = input("Date (DD-MM-YYYY): ")
    time_text = input("Time (HH:MM): ")
    print(scheduler.book(patient, doctor, date, time_text)[1])


def reschedule_menu(scheduler):
    appt_id = input("Appointment ID: ")
    new_date = input("New date (DD-MM-YYYY): ")
    new_time = input("New time (HH:MM): ")
    print(scheduler.reschedule(appt_id, new_date, new_time)[1])


def cancel_menu(scheduler):
    appt_id = input("Appointment ID: ")
    print(scheduler.cancel(appt_id)[1])


def main():
    scheduler = AppointmentScheduler()
    while True:
        print(MENU)
        choice = input("Enter your choice (1-5): ").strip()
        if choice == "1":
            book_menu(scheduler)
        elif choice == "2":
            print(scheduler.view_all()[1])
        elif choice == "3":
            reschedule_menu(scheduler)
        elif choice == "4":
            cancel_menu(scheduler)
        elif choice == "5":
            print("Thank you. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 5.")


if __name__ == "__main__":
    main()
