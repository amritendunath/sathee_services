import { query } from '../database/db.js'

async function checkAvailability(query_date, doctor_name, hospital_name) {
    try {
        const next_date = query_date.slice(0, -2) + String(parseInt(query_date.slice(-2)) + 1).padStart(2, '0');
        const text = `
            SELECT * 
            FROM new_tablee 
            WHERE doctor_name = $2 
                AND hospital_name = $3 
                AND date_slot >= $1 
                AND date_slot < $4 
                AND is_available = $5
        `;
        const values = [query_date, doctor_name.toLowerCase(), hospital_name.toLowerCase(), next_date, 'true']; // Ensure lowercase and correct date range
        const result = await query(text, values)
        return result.rows
    } catch (err) {
        console.error('Error checking availability:', err);
        throw err;
    }
}

async function patient_exists(patient_to_attend) {
    try {
        const text = `
            SELECT date_slot, doctor_name, hospital_name
            FROM new_tablee
            WHERE patient_to_attend = $1
            AND is_available = false
        `;
        const values = [patient_to_attend];

        const result = await query(text, values)
        if (result.rows.length > 0) {
            console.log(`Patient ${patient_to_attend} exists with slots:`, result.rows.map(row => row.date_slot));
            return result.rows; // Return the matching rows
        } else {
            console.log(`Patient ${patient_to_attend} does not exist.`);
            return false;
        }
    } catch (error) {
        console.error(`Error checking patient existence: ${error}`);
        throw error;
    }
}

async function update_appointment_status(query_date, doctor_name, hospital_name, patient_to_attend) {
    const text = `
        UPDATE new_tablee 
        SET is_available = 'false',
            patient_to_attend = $4
        WHERE date_slot = $1
            AND doctor_name = $2
            AND hospital_name = $3
            AND is_available = 'true'
        RETURNING date_slot, doctor_name, hospital_name, is_available, patient_to_attend;
    `;
    const values = [query_date, doctor_name.toLowerCase(), hospital_name.toLowerCase(), patient_to_attend];

    try {
        const result = await query(text, values)
        if (result.rows.length > 0) {
            console.log('Appointment updated:', result.rows);
            return result.rows; // Return the updated rows
        } else {
            console.log('No appointment updated.');
            return false;
        }
    } catch (error) {
        console.error(`Error updating appointment status: ${error}`);
        throw error;
    }
}

async function cancel_appointment(query_date, doctor_name, hospital_name, patient_to_attend) {
    // Implementation for cancelling an appointment
    // This would likely involve setting `is_available` to true and clearing the `patient_to_attend` field
    // Adapt the SQL query accordingly
    const text = `
      UPDATE new_tablee 
      SET is_available = 'true',
          patient_to_attend = null
      WHERE date_slot = $1
          AND doctor_name = $2
          AND hospital_name = $3
          AND patient_to_attend = $4
          AND is_available = 'false'
      RETURNING date_slot, doctor_name, hospital_name, is_available, patient_to_attend;
    `;
    const values = [query_date, doctor_name, hospital_name, patient_to_attend];
    try {
        const result = await query(text, values)
        // Placeholder logic - replace with actual cancellation logic
        // console.log(`Attempting to cancel appointment for ${patient_to_attend} on ${query_date}`);
        console.log('Appointment canceled:', result.rows);
        return true; // Indicate success or failure based on the operation
    } catch (error) {
        console.error(`Error cancelling appointment: ${error}`);
        return false;
    }
}

async function get_doctor_info_by_hospital_name(hospital_name) {
    try {
        const text = `SELECT DISTINCT doctor_name 
                        FROM new_tablee 
                        WHERE hospital_name = $1`
        const values = [hospital_name];

        const result = await query(text, values)
        return result.rows.map(row => row.doctor_name); // Extract doctor names
    } catch (err) {
        console.error('Error fetching doctor info:', err);
        throw err;
    }
}

async function booked_appointment_of_user(user_id) {
  try {
    const text = `
      SELECT doctor_name, specialization, hospital_name, date_slot
      FROM new_tablee
      WHERE patient_to_attend = $1
    `;
    const values = [user_id];
    const result = await query(text, values);

    console.log('booked appointments', result.rows); // Log the data for debugging
    return result.rows; // Return the appointment data

  } catch (error) {
    console.error("Error fetching booked appointments:", error);
    throw error; // Propagate the error for handling in the calling function
  }
}
export {
    checkAvailability,
    patient_exists,
    update_appointment_status,
    cancel_appointment,
    get_doctor_info_by_hospital_name,
    booked_appointment_of_user
};