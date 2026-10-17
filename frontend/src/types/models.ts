/**
 * Entity shapes as serialized by the Flask API (User.to_dict / to_summary,
 * serialize_listing, serialize_message). Dates are HTTP-date strings.
 */
export type UserSummary = {
  id: number;
  name: string | null;
  city: string | null;
  state: string | null;
  avatar_url: string | null;
};

/** Mirrors STATUS_* in app/models/user.py; pending users can't publish listings. */
export type UserStatus = 'active' | 'pending';

/** Another user's profile, as GET /api/v1/users/:id returns it (User.to_public_dict). */
export type PublicUser = UserSummary & {
  last_seen: string | null;
};

/** Your own account (User.to_dict), from login, /auth/me and profile updates. */
export type User = UserSummary & {
  email: string | null;
  /** Set when the user uploaded a picture; null = generated identicon. */
  avatar_src: string | null;
  role: string;
  status: UserStatus;
  last_seen: string | null;
  timestamp: string;
};

export type Listing = {
  id: number;
  title: string;
  body: string;
  price: number;
  condition: string;
  user_id: number;
  timestamp: string;
  /** Cover image: the first of `image_urls`. */
  image_url: string | null;
  image_urls: string[];
  tags: string[];
  author: UserSummary | null;
};

export type Message = {
  id: number;
  sender_id: number;
  recipient_id: number;
  listing_id: number | null;
  subject: string;
  body: string;
  timestamp: string;
  sender: UserSummary | null;
  recipient: UserSummary | null;
  listing: { id: number; title: string } | null;
};
