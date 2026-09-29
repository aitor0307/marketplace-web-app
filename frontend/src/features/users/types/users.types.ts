/** Mirrors UpdateUserPayload in app/schemas/users.py (partial update). */
export type UpdateProfileRequest = {
  name?: string;
  email?: string;
  state?: string;
  city?: string;
};
