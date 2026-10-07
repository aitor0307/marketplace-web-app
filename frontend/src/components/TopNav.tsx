import {
  Avatar,
  Box,
  Button,
  Flex,
  HStack,
  Image,
  Link,
  Menu,
  MenuButton,
  MenuDivider,
  MenuItem,
  MenuList,
  Text,
} from '@chakra-ui/react';
import { useTranslation } from 'react-i18next';
import { HiOutlinePlusCircle, HiOutlineSquares2X2 } from 'react-icons/hi2';
import { Link as RouterLink, NavLink, useNavigate } from 'react-router-dom';
import { LanguageSwitcher } from '@/components/LanguageSwitcher';
import { ROUTES, paths } from '@/config/constants';
import { useLogout } from '@/features/auth/hooks/useAuth';
import { useSessionStore } from '@/store/sessionStore';

const navLinkSx = {
  '&.active': { bg: 'primary.50', color: 'primary.700', fontWeight: 700 },
};

export function TopNav() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const user = useSessionStore((s) => s.user);
  const logout = useLogout();

  const onLogout = () => {
    logout();
    navigate(ROUTES.home);
  };

  return (
    <Box
      as="header"
      position="sticky"
      top={0}
      zIndex={20}
      bg="rgba(255, 255, 255, 0.92)"
      backdropFilter="saturate(180%) blur(8px)"
      borderBottomWidth="1px"
      borderColor="brand.border"
    >
      <Flex
        maxW="1200px"
        mx="auto"
        px={{ base: 4, md: 8 }}
        h="64px"
        align="center"
        gap={{ base: 2, md: 6 }}
      >
        <Link
          as={RouterLink}
          to={ROUTES.home}
          display="flex"
          alignItems="center"
          gap={2}
          flexShrink={0}
        >
          <Image src="/logo.png" alt="" boxSize="28px" objectFit="contain" />
          <Text fontWeight={700} color="brand.primary" display={{ base: 'none', sm: 'block' }}>
            {t('common.appName')}
          </Text>
        </Link>

        <HStack as="nav" spacing={1} flex="1">
          <Button
            as={NavLink}
            to={ROUTES.home}
            end
            variant="ghost"
            size="sm"
            leftIcon={<HiOutlineSquares2X2 />}
            sx={navLinkSx}
          >
            <Box as="span" display={{ base: 'none', md: 'inline' }}>
              {t('nav.listings')}
            </Box>
          </Button>
          <Button
            as={NavLink}
            to={ROUTES.newListing}
            variant="ghost"
            size="sm"
            leftIcon={<HiOutlinePlusCircle />}
            sx={navLinkSx}
          >
            <Box as="span" display={{ base: 'none', md: 'inline' }}>
              {t('nav.sell')}
            </Box>
          </Button>
        </HStack>

        <HStack spacing={3}>
          <LanguageSwitcher />
          {user ? (
            <Menu placement="bottom-end">
              <MenuButton aria-label={t('nav.account')}>
                <Avatar
                  size="sm"
                  name={user.name ?? undefined}
                  src={user.avatar_url ?? undefined}
                />
              </MenuButton>
              <MenuList fontSize="sm">
                <MenuItem as={RouterLink} to={paths.user(user.id)}>
                  {t('nav.profile')}
                </MenuItem>
                <MenuItem as={RouterLink} to={ROUTES.editProfile}>
                  {t('nav.editProfile')}
                </MenuItem>
                <MenuDivider />
                <MenuItem onClick={onLogout}>{t('nav.logout')}</MenuItem>
              </MenuList>
            </Menu>
          ) : (
            <HStack spacing={1}>
              <Button as={RouterLink} to={ROUTES.login} variant="ghost" size="sm">
                {t('nav.login')}
              </Button>
              <Button
                as={RouterLink}
                to={ROUTES.register}
                variant="accent"
                size="sm"
                display={{ base: 'none', sm: 'inline-flex' }}
              >
                {t('nav.register')}
              </Button>
            </HStack>
          )}
        </HStack>
      </Flex>
    </Box>
  );
}
