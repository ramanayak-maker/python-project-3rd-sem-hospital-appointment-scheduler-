from datetime import datetime

appointments = {}
next_id_number = 101
DOCTORS = ["Dr. Mehta", "Dr. Rao"]


def generate_id():
    global next_id_number
    new_id = "A" + str(next_id_number)
    next_id_number += 1
    return new_id


def is_valid_date(date_text):
    try:
        datetime.strptime(date_text, "%d-%m-%Y")
        return True
    except ValueError:
        return False


def is_valid_time(time_text):
    try:
        t = datetime.strptime(time_text, "%H:%M")
    except ValueError:
        return False
    minutes = t.hour * 60 + t.minute
    if minutes < 9 * 60 or minutes > 16 * 60 + 30:
        return False
    if t.minute not in (0, 30):
        return False
    return True


def find_doctor(name):
    for doc in DOCTORS:
        if doc.lower() == name.lower():
            return doc
    return None


def doctor_is_busy(doctor, date, time, ignore_id=None):
    for appt_id, d in appointments.items():
        if appt_id == ignore_id:
            continue
        if d["doctor"] == doctor and d["date"] == date and d["time"] == time:
            return True
    return False


def book_appointment():
    patient = input("Patient: ").strip()
    doctor_input = input("Doctor: ").strip()
    date = input("Date: ").strip()
    time = input("Time: ").strip()

    if patient == "":
        print("Patient name cannot be empty.")
        return
    doctor = find_doctor(doctor_input)
    if doctor is None:
        print("Invalid doctor. Available doctors: " + ", ".join(DOCTORS))
        return
    if not is_valid_date(date):
        print("Invalid date. Please enter the date as DD-MM-YYYY.")
        return
    if not is_valid_time(time):
        print("Invalid time. Slots are 30 minutes, from 09:00 to 16:30 (HH:MM).")
        return
    if doctor_is_busy(doctor, date, time):
        print("Slot unavailable: " + doctor + " already has an appointment on "
              + date + " at " + time + ".")
        return

    appt_id = generate_id()
    appointments[appt_id] = {"patient": patient, "doctor": doctor,
                             "date": date, "time": time}
    print("Appointment booked. ID: " + appt_id + " | " + patient + " | "
          + doctor + " | " + date + " " + time)


def view_all():
    for appt_id, d in appointments.items():
        print(appt_id + " | " + d["patient"] + " | " + d["doctor"]
              + " | " + d["date"] + " " + d["time"])
    print("Total appointments: " + str(len(appointments)))


def reschedule_appointment():
    appt_id = input("ID: ").strip().upper()
    if appt_id not in appointments:
        print("Appointment ID not found.")
        return
    new_date = input("New date: ").strip()
    new_time = input("New time: ").strip()

    if not is_valid_date(new_date):
        print("Invalid date. Please enter the date as DD-MM-YYYY.")
        return
    if not is_valid_time(new_time):
        print("Invalid time. Slots are 30 minutes, from 09:00 to 16:30 (HH:MM).")
        return
    doctor = appointments[appt_id]["doctor"]
    if doctor_is_busy(doctor, new_date, new_time, ignore_id=appt_id):
        print("Slot unavailable: " + doctor + " already has an appointment on "
              + new_date + " at " + new_time + ".")
        return

    appointments[appt_id]["date"] = new_date
    appointments[appt_id]["time"] = new_time
    print("Appointment " + appt_id + " rescheduled to "
          + new_date + " " + new_time + ".")


def cancel_appointment():
    appt_id = input("ID: ").strip().upper()
    if appt_id in appointments:
        del appointments[appt_id]
        print("Appointment " + appt_id + " cancelled.")
    else:
        print("Appointment ID not found.")


def show_menu():
    print()
    print("===== Hospital Appointment Scheduler =====")
    print("1. Book")
    print("2. View all")
    print("3. Reschedule")
    print("4. Cancel")
    print("5. Exit")


def main():
    while True:
        show_menu()
        choice = input("Menu option: ").strip()
        if choice == "1":
            book_appointment()
        elif choice == "2":
            view_all()
        elif choice == "3":
            reschedule_appointment()
        elif choice == "4":
            cancel_appointment()
        elif choice == "5":
            print("Thank you. Goodbye!")
            break
        else:
            print("Invalid option. Please choose 1-5.")


main()
