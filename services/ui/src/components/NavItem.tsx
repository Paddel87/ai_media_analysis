import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { IconType } from 'react-icons';
import { Box, Flex, Icon, Text, useColorModeValue } from '@chakra-ui/react';

interface NavItemProps {
  icon: IconType;
  children: React.ReactNode;
  to: string;
}

const NavItem: React.FC<NavItemProps> = ({ icon, children, to }) => {
  const location = useLocation();
  const isActive = location.pathname === to;

  return (
    <Link to={to} style={{ textDecoration: 'none' }}>
      <Flex
        align="center"
        p="4"
        mx="4"
        borderRadius="lg"
        role="group"
        cursor="pointer"
        bg={isActive ? useColorModeValue('blue.50', 'blue.900') : 'transparent'}
        color={isActive ? useColorModeValue('blue.600', 'blue.200') : useColorModeValue('gray.600', 'gray.300')}
        _hover={{
          bg: useColorModeValue('blue.50', 'blue.900'),
          color: useColorModeValue('blue.600', 'blue.200'),
        }}
      >
        <Icon
          mr="4"
          fontSize="16"
          as={icon}
        />
        <Text>{children}</Text>
      </Flex>
    </Link>
  );
};

export default NavItem; 