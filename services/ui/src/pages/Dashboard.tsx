import React from 'react';
import {
  Box,
  Grid,
  Heading,
  Text,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  SimpleGrid,
  useColorModeValue,
} from '@chakra-ui/react';
import { useQuery } from 'react-query';
import axios from 'axios';

interface DashboardStats {
  totalMedia: number;
  analyzedMedia: number;
  pendingAnalysis: number;
  averageConfidence: number;
  recentAnalyses: Array<{
    id: string;
    title: string;
    confidence: number;
    timestamp: string;
  }>;
}

const Dashboard: React.FC = () => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  const { data: stats, isLoading, error } = useQuery<DashboardStats>(
    'dashboardStats',
    async () => {
      const response = await axios.get('/api/dashboard/stats');
      return response.data;
    }
  );

  if (isLoading) {
    return <Text>Lade Dashboard...</Text>;
  }

  if (error) {
    return <Text>Fehler beim Laden des Dashboards</Text>;
  }

  return (
    <Box p={4}>
      <Heading mb={6}>Dashboard</Heading>

      <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6} mb={8}>
        <Stat
          px={4}
          py={5}
          bg={bgColor}
          shadow="base"
          rounded="lg"
          borderWidth="1px"
          borderColor={borderColor}
        >
          <StatLabel>Gesamt Medien</StatLabel>
          <StatNumber>{stats?.totalMedia}</StatNumber>
          <StatHelpText>
            <StatArrow type="increase" />
            23.36%
          </StatHelpText>
        </Stat>

        <Stat
          px={4}
          py={5}
          bg={bgColor}
          shadow="base"
          rounded="lg"
          borderWidth="1px"
          borderColor={borderColor}
        >
          <StatLabel>Analysierte Medien</StatLabel>
          <StatNumber>{stats?.analyzedMedia}</StatNumber>
          <StatHelpText>
            <StatArrow type="increase" />
            9.05%
          </StatHelpText>
        </Stat>

        <Stat
          px={4}
          py={5}
          bg={bgColor}
          shadow="base"
          rounded="lg"
          borderWidth="1px"
          borderColor={borderColor}
        >
          <StatLabel>Ausstehende Analysen</StatLabel>
          <StatNumber>{stats?.pendingAnalysis}</StatNumber>
          <StatHelpText>
            <StatArrow type="decrease" />
            12.05%
          </StatHelpText>
        </Stat>

        <Stat
          px={4}
          py={5}
          bg={bgColor}
          shadow="base"
          rounded="lg"
          borderWidth="1px"
          borderColor={borderColor}
        >
          <StatLabel>Durchschnittliche Konfidenz</StatLabel>
          <StatNumber>{stats?.averageConfidence.toFixed(2)}%</StatNumber>
          <StatHelpText>
            <StatArrow type="increase" />
            4.05%
          </StatHelpText>
        </Stat>
      </SimpleGrid>

      <Box
        bg={bgColor}
        shadow="base"
        rounded="lg"
        borderWidth="1px"
        borderColor={borderColor}
        p={6}
      >
        <Heading size="md" mb={4}>Letzte Analysen</Heading>
        <Grid templateColumns="repeat(auto-fill, minmax(300px, 1fr))" gap={6}>
          {stats?.recentAnalyses.map((analysis) => (
            <Box
              key={analysis.id}
              p={4}
              borderWidth="1px"
              borderColor={borderColor}
              rounded="md"
            >
              <Text fontWeight="bold">{analysis.title}</Text>
              <Text color="gray.500">Konfidenz: {analysis.confidence.toFixed(2)}%</Text>
              <Text fontSize="sm" color="gray.400">
                {new Date(analysis.timestamp).toLocaleString()}
              </Text>
            </Box>
          ))}
        </Grid>
      </Box>
    </Box>
  );
};

export default Dashboard; 