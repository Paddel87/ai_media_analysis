import React from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import {
  Box,
  Flex,
  VStack,
  HStack,
  IconButton,
  Text,
  useColorMode,
  useDisclosure,
  Drawer,
  DrawerContent,
  useColorModeValue,
} from '@chakra-ui/react';
import { FiMenu, FiMoon, FiSun, FiHome, FiSettings, FiBarChart2 } from 'react-icons/fi';
import { useAuth } from '../contexts/AuthContext';
import NavItem from './NavItem';

const Layout: React.FC = () => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { colorMode, toggleColorMode } = useColorMode();
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <Box minH="100vh" bg={useColorModeValue('gray.50', 'gray.900')}>
      <Box
        ml={{ base: 0, md: 60 }}
        transition=".3s ease"
      >
        <Flex
          h="20"
          alignItems="center"
          mx="8"
          justifyContent="space-between"
        >
          <IconButton
            variant="outline"
            onClick={onOpen}
            aria-label="open menu"
            icon={<FiMenu />}
            display={{ base: 'flex', md: 'none' }}
          />
          <Text
            fontSize="2xl"
            fontFamily="monospace"
            fontWeight="bold"
          >
            AI Media Analysis
          </Text>
          <HStack spacing={4}>
            <IconButton
              aria-label="toggle color mode"
              icon={colorMode === 'light' ? <FiMoon /> : <FiSun />}
              onClick={toggleColorMode}
            />
            <Text>{user?.username}</Text>
          </HStack>
        </Flex>

        <Box p="4">
          <Outlet />
        </Box>
      </Box>

      <Drawer
        autoFocus={false}
        isOpen={isOpen}
        placement="left"
        onClose={onClose}
        returnFocusOnClose={false}
        onOverlayClick={onClose}
        size="full"
      >
        <DrawerContent>
          <VStack
            w="60"
            h="full"
            bg={bgColor}
            borderRight="1px"
            borderColor={borderColor}
            py={5}
            spacing={4}
          >
            <NavItem icon={FiHome} to="/">
              Dashboard
            </NavItem>
            <NavItem icon={FiBarChart2} to="/analysis">
              Medienanalyse
            </NavItem>
            <NavItem icon={FiSettings} to="/settings">
              Einstellungen
            </NavItem>
          </VStack>
        </DrawerContent>
      </Drawer>
    </Box>
  );
};

export default Layout; 