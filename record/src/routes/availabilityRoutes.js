import express from 'express'
import { 
    getAvailability,
    getDoctorInfoByPatient,
    updateAvailability,
    cancelAvailability,
    getDoctorInfo,
    getBookedInfo

 } from '../controller/appointmentController.js'
import verifyToken from '../middleware/authMiddleware.js';



const router = express.Router()

router.post('/booked', verifyToken, getBookedInfo);
router.get('/availability', getAvailability);
router.get('/doctor', getDoctorInfo);
router.get('/patients', getDoctorInfoByPatient);
router.post('/booking', updateAvailability);
router.post('/cancel', cancelAvailability);



export default router;