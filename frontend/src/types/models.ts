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

export type User = UserSummary & {
  email: string | null;
  role: string;
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
  image_url: string | null;
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
