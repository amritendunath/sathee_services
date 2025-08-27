
import {
    checkAvailability,
    patient_exists,
    update_appointment_status,
    cancel_appointment,
    get_doctor_info_by_hospital_name,
    booked_appointment_of_user
} from '../service/availabilityService.js';
import Appointment from '../models/appointment.js';


const getBookedInfo = async (req, res, next) => {
    try {
        const user_id = req.user_id
        const bookedAppointment = await booked_appointment_of_user(user_id)
        if (bookedAppointment && bookedAppointment.length > 0) {
            res.status(200).json({
                message: "Success",
                data: bookedAppointment
            });
        } else {
            res.status(404).json({
                message: "No data found",
                data: []
            });
        }
    } catch (error) {
        next(error)
    }
}



const getAvailability = async (req, res, next) => {
    try {
        const {
            query_date,
            doctor_name,
            hospital_name
        } = req.query;

        const appointments = await checkAvailability(query_date, doctor_name, hospital_name);

        const formattedAppointments = appointments.map(appointment => new Appointment(
            appointment.date_slot,
            appointment.doctor_name,
            appointment.hospital_name,
            appointment.patient_to_attend,
            appointment.is_available
        ));
        if (formattedAppointments && formattedAppointments.length > 0) {
            res.status(200).json({
                message: "Success",
                data: formattedAppointments
            });
        } else {
            res.status(404).json({
                message: "No data found",
                data: []
            });
        }
    } catch (error) {
        next(error); // Pass error to error handling middleware
    }
};

const getDoctorInfoByPatient = async (req, res, next) => {
    try {
        const {
            patient_to_attend
        } = req.query;
        const result = await patient_exists(patient_to_attend);
        if (result && result.length > 0) {
            res.status(200).json({
                message: "Success",
                data: result
            });
        } else {
            res.status(404).json({
                message: "No data found",
                data: []
            });
        }
    } catch (error) {
        next(error);
    }
};

const updateAvailability = async (req, res, next) => {
    try {
        const {
            query_date,
            doctor_name,
            hospital_name,
            patient_to_attend
        } = req.query;
        console.log('query_date:', query_date);
        console.log('doctor_name:', doctor_name);
        console.log('hospital_name:', hospital_name);
        console.log('patient_to_attend:', patient_to_attend);
        const result = await update_appointment_status(query_date, doctor_name, hospital_name, patient_to_attend);
        if (result) {
            res.status(200).json({
                message: "Success",
                data: {
                    appointment_booked: true,
                    slot: query_date
                }
            });
        } else {
            res.status(400).json({
                message: "Failed to book appointment",
                data: {
                    appointment_booked: false,
                    reason: "Slot not available or already booked"
                }
            });
        }
    } catch (error) {
        next(error);
    }
};

const cancelAvailability = async (req, res, next) => {
    try {
        const {
            query_date,
            doctor_name,
            hospital_name,
            patient_to_attend
        } = req.query;
        const result = await cancel_appointment(query_date, doctor_name, hospital_name, patient_to_attend);
        if (result) {
            res.status(200).json({
                message: "Success",
                data: {
                    appointment_cancelled: true,
                    slot: query_date
                }
            });
        } else {
            res.status(400).json({
                message: "Failed to cancel appointment",
                data: {
                    appointment_cancelled: false,
                    reason: "Slot not available or already booked"
                }
            });
        }
    } catch (error) {
        next(error);
    }
};

const getDoctorInfo = async (req, res, next) => {
    try {
        const { hospital_name } = req.query;
        const result = await get_doctor_info_by_hospital_name(hospital_name);
        if (result && result.length > 0) {
            res.status(200).json({
                message: "Success",
                data: result
            });
        } else {
            res.status(404).json({
                message: "No data found",
                data: []
            });
        }
    } catch (error) {
        next(error);
    }
};

export {
    getAvailability,
    getDoctorInfoByPatient,
    updateAvailability,
    cancelAvailability,
    getDoctorInfo,
    getBookedInfo
};