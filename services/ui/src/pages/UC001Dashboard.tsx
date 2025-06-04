/**
 * UC-001 Enhanced Manual Analysis - Main Dashboard
 * Version: 1.0.0 - Complete Web Interface for Enhanced Manual Analysis
 * Status: ALPHA 0.6.0 - Power-User-First Strategy
 */

import {
    Alert,
    AlertIcon,
    Badge,
    Box,
    Button,
    Card,
    CardBody,
    CardHeader,
    Container,
    Heading,
    HStack,
    Icon,
    SimpleGrid,
    Spinner,
    Stat,
    StatArrow,
    StatHelpText,
    StatLabel,
    StatNumber,
    Text,
    useColorModeValue,
    useToast,
    VStack
} from '@chakra-ui/react';
import React, { useEffect } from 'react';
import {
    FiActivity,
    FiCpu,
    FiEye,
    FiMonitor,
    FiPlay,
    FiRefreshCw,
    FiSettings,
    FiSquare,
    FiZap
} from 'react-icons/fi';
import { UC001AnalysisForm } from '../components/UC001AnalysisForm';
import { UC001JobList } from '../components/UC001JobList';
import { UC001PipelineControls } from '../components/UC001PipelineControls';
import { UC001ServiceStatus } from '../components/UC001ServiceStatus';
import { useUC001Dashboard } from '../hooks/useUC001Dashboard';

// Types
interface UC001Metrics {
    total_jobs_processed: number;
    completed_jobs: number;
    failed_jobs: number;
    success_rate: number;
    average_pipeline_duration: number;
    active_jobs: number;
    queue_size: number;
}

interface UC001PipelineStatus {
    pipeline_status: string;
    services: Record<string, any>;
    active_jobs: number;
    queue_size: number;
    max_concurrent: number;
    research_mode: boolean;
    power_user_mode: boolean;
    timestamp: string;
}

export const UC001Dashboard: React.FC = () => {
    const toast = useToast();
    const cardBg = useColorModeValue('white', 'gray.800');
    const borderColor = useColorModeValue('gray.200', 'gray.600');

    // UC-001 Dashboard State
    const {
        pipelineStatus,
        metrics,
        isLoading,
        error,
        refreshData,
        submitJob,
        cancelJob
    } = useUC001Dashboard();

    // Auto-refresh every 5 seconds
    useEffect(() => {
        const interval = setInterval(refreshData, 5000);
        return () => clearInterval(interval);
    }, [refreshData]);

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'healthy': return 'green';
            case 'degraded': return 'yellow';
            case 'unhealthy': return 'red';
            default: return 'gray';
        }
    };

    const getServiceHealthIcon = (serviceStatus: any) => {
        if (serviceStatus?.status === 'healthy') return FiActivity;
        if (serviceStatus?.status === 'degraded') return FiEye;
        return FiSquare;
    };

    if (isLoading && !pipelineStatus) {
        return (
            <Container maxW="container.xl" py={8}>
                <VStack spacing={8}>
                    <Spinner size="xl" color="blue.500" />
                    <Text>Loading UC-001 Enhanced Manual Analysis Dashboard...</Text>
                </VStack>
            </Container>
        );
    }

    if (error) {
        return (
            <Container maxW="container.xl" py={8}>
                <Alert status="error">
                    <AlertIcon />
                    Failed to load UC-001 Dashboard: {error}
                </Alert>
            </Container>
        );
    }

    return (
        <Container maxW="container.xl" py={8}>
            <VStack spacing={8} align="stretch">
                {/* Header Section */}
                <Box>
                    <HStack justify="space-between" align="center" mb={4}>
                        <VStack align="start" spacing={1}>
                            <Heading size="lg" color="blue.500">
                                UC-001 Enhanced Manual Analysis
                            </Heading>
                            <Text color="gray.600" fontSize="sm">
                                Pipeline-Orchestrierung für Power-User Research Workflows
                            </Text>
                        </VStack>

                        <HStack spacing={3}>
                            <Badge
                                colorScheme={pipelineStatus?.research_mode ? 'purple' : 'gray'}
                                variant="solid"
                                p={2}
                            >
                                <Icon as={FiZap} mr={1} />
                                Research Mode
                            </Badge>

                            <Badge
                                colorScheme={pipelineStatus?.power_user_mode ? 'blue' : 'gray'}
                                variant="solid"
                                p={2}
                            >
                                <Icon as={FiCpu} mr={1} />
                                Power User
                            </Badge>

                            <Button
                                leftIcon={<FiRefreshCw />}
                                size="sm"
                                onClick={refreshData}
                                isLoading={isLoading}
                                loadingText="Refreshing"
                            >
                                Refresh
                            </Button>
                        </HStack>
                    </HStack>

                    {/* Pipeline Status Alert */}
                    {pipelineStatus && (
                        <Alert
                            status={pipelineStatus.pipeline_status === 'healthy' ? 'success' : 'warning'}
                            borderRadius="md"
                        >
                            <AlertIcon />
                            <VStack align="start" spacing={0}>
                                <Text fontWeight="bold">
                                    Pipeline Status: {pipelineStatus.pipeline_status.toUpperCase()}
                                </Text>
                                <Text fontSize="sm">
                                    {pipelineStatus.active_jobs} active jobs, {pipelineStatus.queue_size} queued
                                    {pipelineStatus.research_mode && ' • Research Mode Active'}
                                </Text>
                            </VStack>
                        </Alert>
                    )}
                </Box>

                {/* Metrics Overview */}
                <SimpleGrid columns={{ base: 2, md: 4 }} spacing={6}>
                    <Card bg={cardBg} borderColor={borderColor}>
                        <CardBody>
                            <Stat>
                                <StatLabel>Total Jobs</StatLabel>
                                <StatNumber>{metrics?.total_jobs_processed || 0}</StatNumber>
                                <StatHelpText>
                                    <StatArrow type="increase" />
                                    All time
                                </StatHelpText>
                            </Stat>
                        </CardBody>
                    </Card>

                    <Card bg={cardBg} borderColor={borderColor}>
                        <CardBody>
                            <Stat>
                                <StatLabel>Success Rate</StatLabel>
                                <StatNumber>
                                    {((metrics?.success_rate || 0) * 100).toFixed(1)}%
                                </StatNumber>
                                <StatHelpText>
                                    {(metrics?.completed_jobs || 0)} / {(metrics?.total_jobs_processed || 0)} completed
                                </StatHelpText>
                            </Stat>
                        </CardBody>
                    </Card>

                    <Card bg={cardBg} borderColor={borderColor}>
                        <CardBody>
                            <Stat>
                                <StatLabel>Avg Duration</StatLabel>
                                <StatNumber>
                                    {(metrics?.average_pipeline_duration || 0).toFixed(1)}s
                                </StatNumber>
                                <StatHelpText>
                                    Pipeline processing time
                                </StatHelpText>
                            </Stat>
                        </CardBody>
                    </Card>

                    <Card bg={cardBg} borderColor={borderColor}>
                        <CardBody>
                            <Stat>
                                <StatLabel>Queue Status</StatLabel>
                                <StatNumber>{metrics?.queue_size || 0}</StatNumber>
                                <StatHelpText>
                                    {metrics?.active_jobs || 0} active jobs
                                </StatHelpText>
                            </Stat>
                        </CardBody>
                    </Card>
                </SimpleGrid>

                {/* Service Status Grid */}
                <Card bg={cardBg} borderColor={borderColor}>
                    <CardHeader>
                        <Heading size="md">UC-001 Service Health</Heading>
                    </CardHeader>
                    <CardBody>
                        <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4}>
                            {pipelineStatus?.services && Object.entries(pipelineStatus.services).map(([serviceName, serviceData]) => (
                                <HStack
                                    key={serviceName}
                                    p={4}
                                    borderRadius="md"
                                    bg={useColorModeValue('gray.50', 'gray.700')}
                                    justify="space-between"
                                >
                                    <HStack>
                                        <Icon
                                            as={getServiceHealthIcon(serviceData)}
                                            color={getStatusColor(serviceData?.status)}
                                        />
                                        <VStack align="start" spacing={0}>
                                            <Text fontWeight="bold" textTransform="capitalize">
                                                {serviceName.replace('_', ' ')}
                                            </Text>
                                            <Text fontSize="sm" color="gray.600">
                                                {serviceData?.status || 'unknown'}
                                            </Text>
                                        </VStack>
                                    </HStack>
                                    <Badge colorScheme={getStatusColor(serviceData?.status)}>
                                        {serviceData?.status || 'unknown'}
                                    </Badge>
                                </HStack>
                            ))}
                        </SimpleGrid>
                    </CardBody>
                </Card>

                {/* Main Dashboard Grid */}
                <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={8}>
                    {/* Analysis Submission Form */}
                    <Card bg={cardBg} borderColor={borderColor}>
                        <CardHeader>
                            <Heading size="md">
                                <Icon as={FiPlay} mr={2} />
                                Submit Analysis Job
                            </Heading>
                        </CardHeader>
                        <CardBody>
                            <UC001AnalysisForm onSubmit={submitJob} />
                        </CardBody>
                    </Card>

                    {/* Pipeline Controls */}
                    <Card bg={cardBg} borderColor={borderColor}>
                        <CardHeader>
                            <Heading size="md">
                                <Icon as={FiSettings} mr={2} />
                                Pipeline Controls
                            </Heading>
                        </CardHeader>
                        <CardBody>
                            <UC001PipelineControls
                                pipelineStatus={pipelineStatus}
                                onRefresh={refreshData}
                            />
                        </CardBody>
                    </Card>
                </SimpleGrid>

                {/* Job List */}
                <Card bg={cardBg} borderColor={borderColor}>
                    <CardHeader>
                        <Heading size="md">
                            <Icon as={FiMonitor} mr={2} />
                            Active & Recent Jobs
                        </Heading>
                    </CardHeader>
                    <CardBody>
                        <UC001JobList onCancelJob={cancelJob} />
                    </CardBody>
                </Card>

                {/* Service Status Details */}
                <UC001ServiceStatus services={pipelineStatus?.services || {}} />
            </VStack>
        </Container>
    );
};
