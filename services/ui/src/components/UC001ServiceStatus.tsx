/**
 * UC-001 Enhanced Manual Analysis - Service Status Component
 * Version: 1.0.0 - Comprehensive Service Health Monitoring
 * Status: ALPHA 0.6.0 - Power-User-First Strategy
 */

import {
    Alert,
    AlertIcon,
    Badge,
    Box,
    Card,
    CardBody,
    CardHeader,
    Code,
    HStack,
    Icon,
    Progress,
    SimpleGrid,
    Text,
    useColorModeValue,
    VStack
} from '@chakra-ui/react';
import React from 'react';
import {
    FiAlertTriangle,
    FiCheck,
    FiClock,
    FiCpu,
    FiDatabase,
    FiEye,
    FiServer,
    FiShirt,
    FiUser,
    FiVideo,
    FiX
} from 'react-icons/fi';

interface UC001ServiceStatusProps {
    services: Record<string, any>;
}

interface ServiceCardProps {
    serviceName: string;
    serviceData: any;
}

const ServiceCard: React.FC<ServiceCardProps> = ({ serviceName, serviceData }) => {
    const cardBg = useColorModeValue('white', 'gray.800');
    const borderColor = useColorModeValue('gray.200', 'gray.600');

    const getServiceIcon = (name: string) => {
        switch (name) {
            case 'person_dossier': return FiUser;
            case 'video_context_analyzer': return FiVideo;
            case 'clothing_analyzer': return FiShirt;
            case 'redis': return FiDatabase;
            case 'control': return FiCpu;
            default: return FiServer;
        }
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'healthy': return FiCheck;
            case 'degraded': return FiEye;
            case 'unhealthy': return FiAlertTriangle;
            case 'unreachable': return FiX;
            default: return FiClock;
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'healthy': return 'green';
            case 'degraded': return 'yellow';
            case 'unhealthy': return 'red';
            case 'unreachable': return 'gray';
            default: return 'gray';
        }
    };

    const getServiceDescription = (name: string) => {
        switch (name) {
            case 'person_dossier':
                return 'Person detection, recognition, and dossier management';
            case 'video_context_analyzer':
                return 'Video context analysis with LLM processing';
            case 'clothing_analyzer':
                return 'Clothing classification with 200+ categories';
            case 'redis':
                return 'Distributed caching and job coordination';
            case 'control':
                return 'Central system control and configuration';
            default:
                return 'UC-001 pipeline service';
        }
    };

    return (
        <Card bg={cardBg} borderColor={borderColor}>
            <CardHeader pb={2}>
                <HStack justify="space-between">
                    <HStack>
                        <Icon as={getServiceIcon(serviceName)} color="blue.500" />
                        <VStack align="start" spacing={0}>
                            <Text fontWeight="bold" textTransform="capitalize">
                                {serviceName.replace('_', ' ')}
                            </Text>
                            <Text fontSize="xs" color="gray.500">
                                {getServiceDescription(serviceName)}
                            </Text>
                        </VStack>
                    </HStack>
                    <VStack align="end" spacing={1}>
                        <HStack>
                            <Icon as={getStatusIcon(serviceData?.status)} />
                            <Badge colorScheme={getStatusColor(serviceData?.status)}>
                                {serviceData?.status || 'unknown'}
                            </Badge>
                        </HStack>
                    </VStack>
                </HStack>
            </CardHeader>

            <CardBody pt={0}>
                <VStack align="stretch" spacing={3}>
                    {/* Service Details */}
                    {serviceData?.details && (
                        <Box>
                            <Text fontWeight="semibold" fontSize="sm" mb={2}>Service Details:</Text>
                            <VStack align="stretch" spacing={1} fontSize="xs">
                                {Object.entries(serviceData.details).map(([key, value]: [string, any]) => (
                                    <HStack key={key} justify="space-between">
                                        <Text color="gray.600" textTransform="capitalize">
                                            {key.replace('_', ' ')}:
                                        </Text>
                                        <Text fontFamily="mono">
                                            {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                                        </Text>
                                    </HStack>
                                ))}
                            </VStack>
                        </Box>
                    )}

                    {/* Error Information */}
                    {serviceData?.error && (
                        <Alert status="error" size="sm">
                            <AlertIcon />
                            <Text fontSize="xs">{serviceData.error}</Text>
                        </Alert>
                    )}

                    {/* Code/Response Time Information */}
                    {serviceData?.code && (
                        <HStack justify="space-between" fontSize="xs">
                            <Text color="gray.600">HTTP Status:</Text>
                            <Badge colorScheme={serviceData.code >= 200 && serviceData.code < 300 ? 'green' : 'red'}>
                                {serviceData.code}
                            </Badge>
                        </HStack>
                    )}

                    {/* UC-001 Specific Metrics */}
                    {serviceName === 'person_dossier' && serviceData?.details && (
                        <Box>
                            <Text fontWeight="semibold" fontSize="sm" mb={1}>Person Dossier Metrics:</Text>
                            <VStack align="stretch" spacing={1} fontSize="xs">
                                {serviceData.details.total_persons && (
                                    <HStack justify="space-between">
                                        <Text>Total Persons:</Text>
                                        <Badge>{serviceData.details.total_persons}</Badge>
                                    </HStack>
                                )}
                                {serviceData.details.active_dossiers && (
                                    <HStack justify="space-between">
                                        <Text>Active Dossiers:</Text>
                                        <Badge>{serviceData.details.active_dossiers}</Badge>
                                    </HStack>
                                )}
                            </VStack>
                        </Box>
                    )}

                    {serviceName === 'clothing_analyzer' && serviceData?.details && (
                        <Box>
                            <Text fontWeight="semibold" fontSize="sm" mb={1}>Clothing Analyzer Metrics:</Text>
                            <VStack align="stretch" spacing={1} fontSize="xs">
                                {serviceData.details.categories_loaded && (
                                    <HStack justify="space-between">
                                        <Text>Categories Loaded:</Text>
                                        <Badge>{serviceData.details.categories_loaded}</Badge>
                                    </HStack>
                                )}
                                {serviceData.details.model_version && (
                                    <HStack justify="space-between">
                                        <Text>Model Version:</Text>
                                        <Code fontSize="xs">{serviceData.details.model_version}</Code>
                                    </HStack>
                                )}
                            </VStack>
                        </Box>
                    )}

                    {serviceName === 'video_context_analyzer' && serviceData?.details && (
                        <Box>
                            <Text fontWeight="semibold" fontSize="sm" mb={1}>Video Context Metrics:</Text>
                            <VStack align="stretch" spacing={1} fontSize="xs">
                                {serviceData.details.llm_enabled && (
                                    <HStack justify="space-between">
                                        <Text>LLM Enabled:</Text>
                                        <Badge colorScheme="green">YES</Badge>
                                    </HStack>
                                )}
                                {serviceData.details.context_cache_size && (
                                    <HStack justify="space-between">
                                        <Text>Cache Size:</Text>
                                        <Badge>{serviceData.details.context_cache_size}</Badge>
                                    </HStack>
                                )}
                            </VStack>
                        </Box>
                    )}
                </VStack>
            </CardBody>
        </Card>
    );
};

export const UC001ServiceStatus: React.FC<UC001ServiceStatusProps> = ({ services }) => {
    const healthyServices = Object.values(services).filter((service: any) => service?.status === 'healthy').length;
    const totalServices = Object.keys(services).length;
    const healthPercentage = totalServices > 0 ? (healthyServices / totalServices) * 100 : 0;

    return (
        <VStack spacing={6} align="stretch">
            {/* Overall Health Summary */}
            <Box>
                <HStack justify="space-between" mb={3}>
                    <Text fontWeight="bold" fontSize="lg">
                        UC-001 Service Health Overview
                    </Text>
                    <HStack>
                        <Text fontSize="sm" color="gray.600">
                            {healthyServices}/{totalServices} Healthy
                        </Text>
                        <Badge colorScheme={healthPercentage === 100 ? 'green' : healthPercentage >= 70 ? 'yellow' : 'red'}>
                            {healthPercentage.toFixed(0)}%
                        </Badge>
                    </HStack>
                </HStack>

                <Progress
                    value={healthPercentage}
                    colorScheme={healthPercentage === 100 ? 'green' : healthPercentage >= 70 ? 'yellow' : 'red'}
                    hasStripe
                    isAnimated={healthPercentage < 100}
                />
            </Box>

            {/* Overall Status Alert */}
            {healthPercentage < 100 && (
                <Alert status={healthPercentage >= 70 ? 'warning' : 'error'}>
                    <AlertIcon />
                    <VStack align="start" spacing={0}>
                        <Text fontWeight="bold" fontSize="sm">
                            {healthPercentage >= 70 ? 'Service Degradation Detected' : 'Critical Service Issues'}
                        </Text>
                        <Text fontSize="xs">
                            {totalServices - healthyServices} service(s) are not fully operational.
                            Check individual service status below.
                        </Text>
                    </VStack>
                </Alert>
            )}

            {totalServices === 0 && (
                <Alert status="warning">
                    <AlertIcon />
                    <Text>No UC-001 services detected. Check pipeline connectivity.</Text>
                </Alert>
            )}

            {/* Service Grid */}
            {totalServices > 0 && (
                <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={4}>
                    {Object.entries(services).map(([serviceName, serviceData]) => (
                        <ServiceCard
                            key={serviceName}
                            serviceName={serviceName}
                            serviceData={serviceData}
                        />
                    ))}
                </SimpleGrid>
            )}

            {/* Service Dependencies */}
            <Box>
                <Text fontWeight="bold" mb={3}>UC-001 Service Dependencies</Text>
                <VStack align="stretch" spacing={2} fontSize="sm">
                    <HStack justify="space-between" p={2} borderRadius="md" bg="gray.50">
                        <Text>person_dossier</Text>
                        <HStack>
                            <Text fontSize="xs">depends on:</Text>
                            <Badge size="sm">redis</Badge>
                            <Badge size="sm">control</Badge>
                        </HStack>
                    </HStack>

                    <HStack justify="space-between" p={2} borderRadius="md" bg="gray.50">
                        <Text>video_context_analyzer</Text>
                        <HStack>
                            <Text fontSize="xs">depends on:</Text>
                            <Badge size="sm">redis</Badge>
                            <Badge size="sm">control</Badge>
                            <Badge size="sm">person_dossier</Badge>
                        </HStack>
                    </HStack>

                    <HStack justify="space-between" p={2} borderRadius="md" bg="gray.50">
                        <Text>clothing_analyzer</Text>
                        <HStack>
                            <Text fontSize="xs">depends on:</Text>
                            <Badge size="sm">redis</Badge>
                            <Badge size="sm">control</Badge>
                            <Badge size="sm">person_dossier</Badge>
                        </HStack>
                    </HStack>
                </VStack>
            </Box>
        </VStack>
    );
};
