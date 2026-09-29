import { Box } from '@chakra-ui/react';
import { Outlet } from 'react-router-dom';
import { TopNav } from '@/components/TopNav';

export function MainLayout() {
  return (
    <Box minH="100dvh" bg="brand.pageBg">
      <TopNav />
      <Outlet />
    </Box>
  );
}
