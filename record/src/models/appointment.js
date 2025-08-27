
class Appointment {
    constructor(date_slot, doctor_name, hospital_name, patient_to_attend, is_available) {
        this.date_slot = date_slot;
        this.doctor_name = doctor_name;
        this.hospital_name = hospital_name;
        this.patient_to_attend = patient_to_attend;
        this.is_available = is_available;
    }
}

export default Appointment;