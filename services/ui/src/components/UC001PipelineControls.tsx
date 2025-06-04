/**
 * UC-001 Enhanced Manual Analysis - Pipeline Controls Component
 * Version: 1.0.0 - System Management & Debugging Tools
 * Status: ALPHA 0.6.0 - Power-User-First Strategy
 */

import {
    Alert,
    AlertIcon,
    Badge,
    Box,
    Button,
    Code,
    Divider,
    HStack,
    Icon,
    Modal,
    ModalBody,
    ModalCloseButton,
    ModalContent,
    ModalHeader,
    ModalOverlay,
    Text,
    useColorModeValue,
    useDisclosure,
    useToast,
    VStack
} from '@chakra-ui/react';
import React, { useState } from 'react';
import {
    FiActivity,
    FiCpu,
    FiRefreshCw,
    FiTool,
    FiZap
} from 'react-icons/fi';
import { UC001PipelineStatus, useUC001Dashboard } from '../hooks/useUC001Dashboard';

interface UC001PipelineControlsProps {
    pipelineStatus: UC001PipelineStatus | null;
    onRefresh: () => Promise<void>;
}

interface DebugModalProps {
    isOpen: boolean;
    onClose: () => void;
}

const DebugModal: React.FC<DebugModalProps> = ({ isOpen, onClose }) => {
    const { validateServices, getQueueDebugInfo } = useUC001Dashboard();
    const [debugData, setDebugData] = useState<any>(null);
    const [queueData, setQueueData] = useState<any>(null);
    const [isLoading, setIsLoading] = useState(false);
    const toast = useToast();

    const fetchDebugData = async () => {
        setIsLoading(true);
        try {
            const [services, queue] = await Promise.all([
                validateServices(),
                getQueueDebugInfo()
            ]);
            setDebugData(services);
            setQueueData(queue);
        } catch (error: any) {
            toast({
                title: 'Debug Data Fetch Failed',
                description: error.message,
                status: 'error',
                duration: 5000,
                isClosable: true,
            });
        } finally {
            setIsLoading(false);
        }
    };

    React.useEffect(() => {
        if (isOpen) {
            fetchDebugData();
        }
    }, [isOpen]);

    return (
        <Modal isOpen={isOpen} onClose={onClose} size="xl">
            <ModalOverlay />
            <ModalContent maxH="80vh" overflowY="auto">
                <ModalHeader>
                    <HStack>
                        <Icon as={FiTool} />
                        <Text>UC-001 Pipeline Debug Information</Text>
                    </HStack>
                </ModalHeader>
                <ModalCloseButton />
                <ModalBody pb={6}>
                    <VStack spacing={6} align="stretch">
                        {/* Service Connectivity */}
                        <Box>
                            <Text fontWeight="bold" mb={3}>Service Connectivity</Text>
                            {debugData ? (
                                <VStack align="stretch" spacing={2}>
                                    {Object.entries(debugData.services || {}).map(([serviceName, serviceData]: [string, any]) => (
                                        <HStack key={serviceName} justify="space-between" p={3} borderRadius="md" bg="gray.50">
                                            <Text>{serviceName}</Text>
                                            <Badge colorScheme={serviceData.status === 'healthy' ? 'green' : 'red'}>
                                                {serviceData.status}
                                            </Badge>
                                        </HStack>
                                    ))}
                                    <Code display="block" whiteSpace="pre-wrap" fontSize="xs" p={3}>
                                        {JSON.stringify(debugData, null, 2)}
                                    </Code>
                                </VStack>
                            ) : (
                                <Text fontSize="sm" color="gray.500">Loading service data...</Text>
                            )}
                        </Box>

                        <Divider />

                        {/* Queue Information */}
                        <Box>
                            <Text fontWeight="bold" mb={3}>Job Queue Status</Text>
                            {queueData ? (
                                <VStack align="stretch" spacing={2}>
                                    <HStack justify="space-between">
                                        <Text>Queue Size:</Text>
                                        <Badge colorScheme="blue">{queueData.queue_size}</Badge>
                                    </HStack>
                                    <Text fontWeight="semibold" fontSize="sm">Queued Jobs:</Text>
                                    <Code display="block" whiteSpace="pre-wrap" fontSize="xs" p={3}>
                                        {JSON.stringify(queueData, null, 2)}
                                    </Code>
                                </VStack>
                            ) : (
                                <Text fontSize="sm" color="gray.500">Loading queue data...</Text>
                            )}
                        </Box>

                        <Button
                            leftIcon={<FiRefreshCw />}
                            onClick={fetchDebugData}
                            isLoading={isLoading}
                            loadingText="Refreshing..."
                        >
                            Refresh Debug Data
                        </Button>
                    </VStack>
                </ModalBody>
            </ModalContent>
        </Modal>
    );
};

export const UC001PipelineControls: React.FC<UC001PipelineControlsProps> = ({
    pipelineStatus,
    onRefresh
}) => {
    const { isOpen, onOpen, onClose } = useDisclosure();
    const { checkServiceHealth } = useUC001Dashboard();
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [isCheckingHealth, setIsCheckingHealth] = useState(false);
    const toast = useToast();

    const cardBg = useColorModeValue('gray.50', 'gray.700');

    const handleRefresh = async () => {
        setIsRefreshing(true);
        try {
            await onRefresh();
            toast({
                title: 'Pipeline Refreshed',
                description: 'Pipeline status has been updated',
                status: 'success',
                duration: 3000,
                isClosable: true,
            });
        } catch (error: any) {
            toast({
                title: 'Refresh Failed',
                description: error.message,
                status: 'error',
                duration: 5000,
                isClosable: true,
            });
        } finally {
            setIsRefreshing(false);
        }
    };

    const handleHealthCheck = async () => {
        setIsCheckingHealth(true);
        try {
            const health = await checkServiceHealth();
            toast({
                title: 'Health Check Complete',
                description: `Pipeline status: ${health.status}`,
                status: health.status === 'healthy' ? 'success' : 'warning',
                duration: 5000,
                isClosable: true,
            });
        } catch (error: any) {
            toast({
                title: 'Health Check Failed',
                description: error.message,
                status: 'error',
                duration: 5000,
                isClosable: true,
            });
        } finally {
            setIsCheckingHealth(false);
        }
    };

    return (
        <VStack spacing={4} align="stretch">
            {/* Pipeline Status Summary */}
            <Box bg={cardBg} p={4} borderRadius="md">
                <Text fontWeight="bold" mb={3}>Pipeline Status</Text>
                <VStack align="stretch" spacing={2}>
                    <HStack justify="space-between">
                        <Text fontSize="sm">Status:</Text>
                        <Badge colorScheme={pipelineStatus?.pipeline_status === 'healthy' ? 'green' : 'yellow'}>
                            {pipelineStatus?.pipeline_status || 'Unknown'}
                        </Badge>
                    </HStack>
                    <HStack justify="space-between">
                        <Text fontSize="sm">Active Jobs:</Text>
                        <Badge colorScheme="blue">
                            {pipelineStatus?.active_jobs || 0}
                        </Badge>
                    </HStack>
                    <HStack justify="space-between">
                        <Text fontSize="sm">Queue Size:</Text>
                        <Badge colorScheme="purple">
                            {pipelineStatus?.queue_size || 0}
                        </Badge>
                    </HStack>
                    <HStack justify="space-between">
                        <Text fontSize="sm">Max Concurrent:</Text>
                        <Badge colorScheme="gray">
                            {pipelineStatus?.max_concurrent || 5}
                        </Badge>
                    </HStack>
                </VStack>
            </Box>

            {/* Mode Indicators */}
            <Box bg={cardBg} p={4} borderRadius="md">
                <Text fontWeight="bold" mb={3}>Active Modes</Text>
                <VStack align="stretch" spacing={2}>
                    <HStack justify="space-between">
                        <HStack>
                            <Icon as={FiZap} color="purple.500" />
                            <Text fontSize="sm">Research Mode:</Text>
                        </HStack>
                        <Badge colorScheme={pipelineStatus?.research_mode ? 'purple' : 'gray'}>
                            {pipelineStatus?.research_mode ? 'ACTIVE' : 'INACTIVE'}
                        </Badge>
                    </HStack>
                    <HStack justify="space-between">
                        <HStack>
                            <Icon as={FiCpu} color="blue.500" />
                            <Text fontSize="sm">Power User Mode:</Text>
                        </HStack>
                        <Badge colorScheme={pipelineStatus?.power_user_mode ? 'blue' : 'gray'}>
                            {pipelineStatus?.power_user_mode ? 'ACTIVE' : 'INACTIVE'}
                        </Badge>
                    </HStack>
                </VStack>
            </Box>

            <Divider />

            {/* Control Buttons */}
            <VStack spacing={3} align="stretch">
                <Text fontWeight="bold" fontSize="sm" color="gray.600">
                    Pipeline Controls
                </Text>

                <Button
                    leftIcon={<FiRefreshCw />}
                    onClick={handleRefresh}
                    isLoading={isRefreshing}
                    loadingText="Refreshing..."
                    colorScheme="blue"
                    size="sm"
                >
                    Refresh Pipeline Status
                </Button>

                <Button
                    leftIcon={<FiActivity />}
                    onClick={handleHealthCheck}
                    isLoading={isCheckingHealth}
                    loadingText="Checking..."
                    variant="outline"
                    size="sm"
                >
                    Run Health Check
                </Button>

                <Button
                    leftIcon={<FiTool />}
                    onClick={onOpen}
                    variant="outline"
                    size="sm"
                    colorScheme="purple"
                >
                    Debug Information
                </Button>
            </VStack>

            {/* System Information */}
            <Box bg={cardBg} p={4} borderRadius="md">
                <Text fontWeight="bold" mb={3}>System Information</Text>
                <VStack align="stretch" spacing={2} fontSize="sm">
                    <HStack justify="space-between">
                        <Text>Services:</Text>
                        <Text>{pipelineStatus?.services ? Object.keys(pipelineStatus.services).length : 0}</Text>
                    </HStack>
                    <HStack justify="space-between">
                        <Text>Last Update:</Text>
                        <Text>
                            {pipelineStatus?.timestamp
                                ? new Date(pipelineStatus.timestamp).toLocaleTimeString()
                                : 'Never'
                            }
                        </Text>
                    </HStack>
                </VStack>
            </Box>

            {/* Warnings/Alerts */}
            {pipelineStatus && pipelineStatus.pipeline_status !== 'healthy' && (
                <Alert status="warning" size="sm">
                    <AlertIcon />
                    <Text fontSize="sm">
                        Pipeline is not fully healthy. Check service status for details.
                    </Text>
                </Alert>
            )}

            {pipelineStatus && pipelineStatus.active_jobs >= pipelineStatus.max_concurrent && (
                <Alert status="info" size="sm">
                    <AlertIcon />
                    <Text fontSize="sm">
                        Pipeline is running at maximum capacity ({pipelineStatus.max_concurrent} jobs).
                    </Text>
                </Alert>
            )}

            {/* Debug Modal */}
            <DebugModal isOpen={isOpen} onClose={onClose} />
        </VStack>
    );
};
