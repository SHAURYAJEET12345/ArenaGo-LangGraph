export interface Turf {
  id: string;
  name: string;
  ownerId: string;
}
export interface Booking {
  id: string;
  turfId: string;
  userId: string;
  status: 'pending' | 'completed' | 'cancelled';
}
