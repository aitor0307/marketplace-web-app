import { Route, Routes } from 'react-router-dom';
import { LegacyRedirect } from '@/app/LegacyRedirect';
import { MainLayout } from '@/app/MainLayout';
import { NotFoundScreen } from '@/app/NotFoundScreen';
import { RequireAuth, RequireGuest } from '@/app/RequireAuth';
import { ROUTES, paths } from '@/config/constants';
import { LoginScreen, RegisterScreen } from '@/features/auth';
import { ListingDetailScreen, ListingsScreen, NewListingScreen } from '@/features/listings';
import { SendMessageScreen } from '@/features/messages';
import { EditProfileScreen, UserProfileScreen } from '@/features/users';

export function AppRouter() {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route path={ROUTES.home} element={<ListingsScreen />} />
        <Route path={ROUTES.listing} element={<ListingDetailScreen />} />
        <Route path={ROUTES.user} element={<UserProfileScreen />} />

        <Route element={<RequireGuest />}>
          <Route path={ROUTES.login} element={<LoginScreen />} />
          <Route path={ROUTES.register} element={<RegisterScreen />} />
        </Route>

        <Route element={<RequireAuth />}>
          <Route path={ROUTES.newListing} element={<NewListingScreen />} />
          <Route path={ROUTES.editProfile} element={<EditProfileScreen />} />
          <Route path={ROUTES.sendMessage} element={<SendMessageScreen />} />
        </Route>

        {/* Deprecated Jinja view URLs → SPA routes */}
        <Route path="/index" element={<LegacyRedirect to={() => ROUTES.home} />} />
        <Route path="/new_listing" element={<LegacyRedirect to={() => ROUTES.newListing} />} />
        <Route path="/edit_profile" element={<LegacyRedirect to={() => ROUTES.editProfile} />} />
        <Route
          path="/listing/:listingId"
          element={<LegacyRedirect to={(p) => paths.listing(p.listingId ?? '')} />}
        />
        <Route
          path="/user/:userId"
          element={<LegacyRedirect to={(p) => paths.user(p.userId ?? '')} />}
        />
        <Route
          path="/message/:userId"
          element={<LegacyRedirect to={(p) => `/users/${p.userId ?? ''}/message`} />}
        />

        <Route path="*" element={<NotFoundScreen />} />
      </Route>
    </Routes>
  );
}
