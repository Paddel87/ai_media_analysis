/**
 * AI Media Analysis - Main App Component
 * Version: 1.0.0 + UC-001 Enhanced Manual Analysis Integration
 * Status: ALPHA 0.6.0 - Power-User-First Strategy
 */

import { Badge, Box, Button, ChakraProvider, HStack, Icon, Text, useColorModeValue, VStack } from '@chakra-ui/react';
import React from 'react';
import { FiActivity, FiCpu, FiHome, FiSettings, FiZap } from 'react-icons/fi';
import { Navigate, Route, BrowserRouter as Router, Routes } from 'react-router-dom';

// Import UC-001 Dashboard
import { UC001Dashboard } from './pages/UC001Dashboard';

// Simple theme
const theme = {
  config: {
    initialColorMode: 'light'
  }
};

// Navigation Component
const Navigation: React.FC = () => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  return (
    <Box
      bg={bgColor}
      borderBottom="1px"
      borderColor={borderColor}
      p={4}
      position="sticky"
      top={0}
      zIndex={1000}
    >
      <HStack justify="space-between" maxW="container.xl" mx="auto">
        <HStack spacing={8}>
          <VStack align="start" spacing={0}>
            <Text fontSize="xl" fontWeight="bold" color="blue.500">
              AI Media Analysis
            </Text>
            <Text fontSize="sm" color="gray.600">
              UC-001 Enhanced Manual Analysis System
            </Text>
          </VStack>

          <HStack spacing={4}>
            <Button
              leftIcon={<Icon as={FiHome} />}
              variant="ghost"
              size="sm"
              as="a"
              href="/"
            >
              Overview
            </Button>
            <Button
              leftIcon={<Icon as={FiActivity} />}
              variant="ghost"
              size="sm"
              as="a"
              href="/uc001"
            >
              UC-001 Dashboard
            </Button>
          </HStack>
        </HStack>

        <HStack spacing={3}>
          <Badge colorScheme="purple" variant="solid" p={2}>
            <Icon as={FiZap} mr={1} />
            Research Mode
          </Badge>
          <Badge colorScheme="blue" variant="solid" p={2}>
            <Icon as={FiCpu} mr={1} />
            Power User
          </Badge>
        </HStack>
      </HStack>
    </Box>
  );
};

// Landing Page Component
const LandingPage: React.FC = () => {
  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  return (
    <Box maxW="container.xl" mx="auto" p={8}>
      <VStack spacing={8} align="stretch">
        <VStack spacing={4} textAlign="center">
          <Text fontSize="4xl" fontWeight="bold" color="blue.500">
            AI Media Analysis System
          </Text>
          <Text fontSize="xl" color="gray.600">
            Advanced Computer Vision & Analysis Pipeline
          </Text>
          <Text maxW="2xl" color="gray.500">
            Hochmodernes System für automatisierte Medienanalyse mit KI-gestützter
            Personen-, Video- und Kleidungsanalyse für Research-Anwendungen.
          </Text>
        </VStack>

        <Box
          bg={cardBg}
          p={8}
          borderRadius="lg"
          border="1px"
          borderColor={borderColor}
          textAlign="center"
        >
          <VStack spacing={6}>
            <Text fontSize="2xl" fontWeight="bold" color="purple.500">
              UC-001 Enhanced Manual Analysis
            </Text>
            <Text color="gray.600">
              Power-User-Interface für erweiterte manuelle Analyse mit vollständiger
              Pipeline-Orchestrierung und Real-time Job-Monitoring.
            </Text>
            <HStack spacing={8}>
              <VStack>
                <Icon as={FiActivity} size="24px" color="blue.500" />
                <Text fontSize="sm" fontWeight="bold">Pipeline Control</Text>
                <Text fontSize="xs" color="gray.500">Complete workflow management</Text>
              </VStack>
              <VStack>
                <Icon as={FiZap} size="24px" color="purple.500" />
                <Text fontSize="sm" fontWeight="bold">Research Mode</Text>
                <Text fontSize="xs" color="gray.500">Unrestricted analysis capabilities</Text>
              </VStack>
              <VStack>
                <Icon as={FiCpu} size="24px" color="green.500" />
                <Text fontSize="sm" fontWeight="bold">Real-time Monitoring</Text>
                <Text fontSize="xs" color="gray.500">Live job status & progress</Text>
              </VStack>
            </HStack>
            <Button
              as="a"
              href="/uc001"
              colorScheme="blue"
              size="lg"
              leftIcon={<Icon as={FiActivity} />}
            >
              Open UC-001 Dashboard
            </Button>
          </VStack>
        </Box>

        {/* Feature Grid */}
        <VStack spacing={4} align="stretch">
          <Text fontSize="xl" fontWeight="bold" textAlign="center">
            System Features
          </Text>
          <Box
            display="grid"
            gridTemplateColumns={{ base: '1fr', md: 'repeat(3, 1fr)' }}
            gap={6}
          >
            <Box bg={cardBg} p={6} borderRadius="md" border="1px" borderColor={borderColor}>
              <VStack align="start" spacing={3}>
                <Icon as={FiActivity} size="32px" color="blue.500" />
                <Text fontWeight="bold">Person Analysis</Text>
                <Text fontSize="sm" color="gray.600">
                  Advanced face recognition, person tracking, and dossier management
                  with high-accuracy detection algorithms.
                </Text>
              </VStack>
            </Box>

            <Box bg={cardBg} p={6} borderRadius="md" border="1px" borderColor={borderColor}>
              <VStack align="start" spacing={3}>
                <Icon as={FiSettings} size="32px" color="purple.500" />
                <Text fontWeight="bold">Video Context Analysis</Text>
                <Text fontSize="sm" color="gray.600">
                  LLM-powered video context understanding with emotion analysis,
                  movement tracking, and scene interpretation.
                </Text>
              </VStack>
            </Box>

            <Box bg={cardBg} p={6} borderRadius="md" border="1px" borderColor={borderColor}>
              <VStack align="start" spacing={3}>
                <Icon as={FiZap} size="32px" color="green.500" />
                <Text fontWeight="bold">Clothing Classification</Text>
                <Text fontSize="sm" color="gray.600">
                  200+ category clothing analysis with material detection,
                  style classification, and hierarchical categorization.
                </Text>
              </VStack>
            </Box>
          </Box>
        </VStack>
      </VStack>
    </Box>
  );
};

// Main App Component
const App: React.FC = () => {
  return (
    <ChakraProvider theme={theme}>
      <Router>
        <Box minH="100vh" bg={useColorModeValue('gray.50', 'gray.900')}>
          <Navigation />
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/uc001" element={<UC001Dashboard />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Box>
      </Router>
    </ChakraProvider>
  );
};

export default App;
