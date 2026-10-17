import { apiClient } from '@/services/apiClient';
import type { UpdateProfileRequest } from '@/features/users/types/users.types';
import type { Listing, PublicUser, User } from '@/types/models';

export const usersApi = {
  get(userId: number): Promise<PublicUser> {
    return apiClient<{ user: PublicUser }>(`/api/v1/users/${userId}`, { auth: false }).then(
      (res) => res.user,
    );
  },

  update(userId: number, payload: UpdateProfileRequest): Promise<User> {
    return apiClient<{ user: User }>(`/api/v1/users/${userId}`, {
      method: 'PUT',
      body: payload,
    }).then((res) => res.user);
  },

  uploadAvatar(userId: number, file: File): Promise<User> {
    const form = new FormData();
    form.append('avatar', file);
    return apiClient<{ user: User }>(`/api/v1/users/${userId}/avatar`, {
      method: 'PUT',
      body: form,
    }).then((res) => res.user);
  },

  removeAvatar(userId: number): Promise<User> {
    return apiClient<{ user: User }>(`/api/v1/users/${userId}/avatar`, {
      method: 'DELETE',
    }).then((res) => res.user);
  },

  listings(userId: number): Promise<Listing[]> {
    return apiClient<{ listings: Listing[] }>(`/api/v1/users/${userId}/listings`, {
      auth: false,
    }).then((res) => res.listings);
  },
};
