import * as functions from "firebase-functions/v1";
import * as admin from "firebase-admin";

admin.initializeApp();

export const onBookingCreate = functions.firestore
  .document("bookings/{bookingId}")
  .onCreate(async (snap, context) => {
    const data = snap.data();
    functions.logger.info("New booking created", data);
  });

export const onBookingCancel = functions.firestore
  .document("bookings/{bookingId}")
  .onUpdate(async (change, context) => {
    const after = change.after.data();
    if (after && after.status === "cancelled") {
      functions.logger.info("Booking cancelled", after);
    }
  });

export const generateEBill = functions.firestore
  .document("bookings/{bookingId}")
  .onUpdate(async (change, context) => {
     const after = change.after.data();
     if(after && after.status === "completed") {
        functions.logger.info("Generating e-bill for", context.params.bookingId);
     }
  });

export const sendBookingReminder = functions.pubsub.schedule("every 1 hours").onRun(async (context) => {
  functions.logger.info("Running booking reminders");
});
