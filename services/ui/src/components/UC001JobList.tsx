/**
 * UC-001 Enhanced Manual Analysis - Job List Component
 * Version: 1.0.0 - Real-time Job Monitoring & Management
 * Status: ALPHA 0.6.0 - Power-User-First Strategy
 */

import {
    Accordion,
    AccordionButton,
    AccordionIcon,
    AccordionItem,
    AccordionPanel,
    Alert,
    AlertIcon,
    Badge,
    Box,
    Button,
    Code,
    Divider,
    HStack,
    Icon,
    Input,
    InputGroup,
    InputLeftElement,
    Modal,
    ModalBody,
    ModalCloseButton,
    ModalContent,
    ModalHeader,
    ModalOverlay,
    Progress,
    Select,
    Spinner,
    Table,
    TableContainer,
    Tbody,
    Td,
    Text,
    Th,
    Thead,
    Tooltip,
    Tr,
    useColorModeValue,
    useDisclosure,
    VStack
} from '@chakra-ui/react';
import React, { useEffect, useState } from 'react';
import {
    FiAlertTriangle,
    FiCheck,
    FiClock,
    FiCpu,
    FiEye,
    FiFilter,
    FiPause,
    FiPlay,
    FiRefreshCw,
    FiSearch,
    FiShirt,
    FiUser,
    FiVideo,
    FiX
} from 'react-icons/fi';
import { UC001Job, useUC001Dashboard } from '../hooks/useUC001Dashboard';

interface UC001JobListProps {
    onCancelJob: (jobId: string) => Promise<void>;
}

interface JobDetailsModalProps {
    isOpen: boolean;
    onClose: () => void;
    job: UC001Job | null;
}

const JobDetailsModal: React.FC<JobDetailsModalProps> = ({ isOpen, onClose, job }) => {
    const { getJobDetails, getJobResults } = useUC001Dashboard();
    const [jobDetails, setJobDetails] = useState<any>(null);
    const [jobResults, setJobResults] = useState<any>(null);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        if (isOpen && job) {
            fetchJobDetails();
        }
    }, [isOpen, job]);

    const fetchJobDetails = async () => {
        if (!job) return;

        setIsLoading(true);
        try {
            const details = await getJobDetails(job.job_id);
            setJobDetails(details);

            // Try to fetch results if job is completed
            if (details.status === 'completed') {
                try {
                    const results = await getJobResults(job.job_id);
                    setJobResults(results);
                } catch (error) {
                    console.warn('Could not fetch job results:', error);
                }
            }
        } catch (error) {
            console.error('Failed to fetch job details:', error);
        } finally {
            setIsLoading(false);
        }
    };

    if (!job) return null;

    return (
        <Modal isOpen={isOpen} onClose={onClose} size="xl">
            <ModalOverlay />
            <ModalContent maxH="80vh" overflowY="auto">
                <ModalHeader>
                    <HStack>
                        <Text>Job Details: {job.job_id}</Text>
                        <Badge colorScheme={getStatusColor(job.status)}>
                            {job.status.toUpperCase()}
                        </Badge>
                    </HStack>
                </ModalHeader>
                <ModalCloseButton />
                <ModalBody pb={6}>
                    {isLoading ? (
                        <VStack spacing={4}>
                            <Spinner />
                            <Text>Loading job details...</Text>
                        </VStack>
                    ) : (
                        <VStack spacing={6} align="stretch">
                            {/* Basic Info */}
                            <Box>
                                <Text fontWeight="bold" mb={2}>Basic Information</Text>
                                <VStack align="stretch" spacing={2} fontSize="sm">
                                    <HStack justify="space-between">
                                        <Text>Job Type:</Text>
                                        <Badge>{job.job_type}</Badge>
                                    </HStack>
                                    <HStack justify="space-between">
                                        <Text>User ID:</Text>
                                        <Text>{job.user_id}</Text>
                                    </HStack>
                                    <HStack justify="space-between">
                                        <Text>Priority:</Text>
                                        <Badge colorScheme={getPriorityColor(job.priority)}>
                                            {job.priority}
                                        </Badge>
                                    </HStack>
                                    <HStack justify="space-between">
                                        <Text>Created:</Text>
                                        <Text>{new Date(job.created_at).toLocaleString()}</Text>
                                    </HStack>
                                    {job.updated_at && (
                                        <HStack justify="space-between">
                                            <Text>Updated:</Text>
                                            <Text>{new Date(job.updated_at).toLocaleString()}</Text>
                                        </HStack>
                                    )}
                                </VStack>
                            </Box>

                            <Divider />

                            {/* Progress Info */}
                            {jobDetails && (
                                <Box>
                                    <Text fontWeight="bold" mb={2}>Progress Information</Text>
                                    <VStack align="stretch" spacing={2}>
                                        {jobDetails.progress !== undefined && (
                                            <Box>
                                                <HStack justify="space-between" mb={1}>
                                                    <Text fontSize="sm">Progress:</Text>
                                                    <Text fontSize="sm">{jobDetails.progress?.toFixed(1)}%</Text>
                                                </HStack>
                                                <Progress value={jobDetails.progress} colorScheme="blue" />
                                            </Box>
                                        )}
                                        {jobDetails.current_step && (
                                            <HStack justify="space-between">
                                                <Text fontSize="sm">Current Step:</Text>
                                                <Badge>{jobDetails.current_step}</Badge>
                                            </HStack>
                                        )}
                                        {jobDetails.error_message && (
                                            <Alert status="error" size="sm">
                                                <AlertIcon />
                                                <Text fontSize="sm">{jobDetails.error_message}</Text>
                                            </Alert>
                                        )}
                                    </VStack>
                                </Box>
                            )}

                            {/* Results (if completed) */}
                            {jobResults && (
                                <>
                                    <Divider />
                                    <Accordion allowToggle>
                                        <AccordionItem>
                                            <AccordionButton>
                                                <Box flex="1" textAlign="left">
                                                    <Text fontWeight="bold">Analysis Results</Text>
                                                </Box>
                                                <AccordionIcon />
                                            </AccordionButton>
                                            <AccordionPanel pb={4}>
                                                <VStack align="stretch" spacing={4}>
                                                    {jobResults.person_id && (
                                                        <HStack justify="space-between">
                                                            <Text>Person ID:</Text>
                                                            <Code>{jobResults.person_id}</Code>
                                                        </HStack>
                                                    )}
                                                    {jobResults.pipeline_duration && (
                                                        <HStack justify="space-between">
                                                            <Text>Duration:</Text>
                                                            <Text>{jobResults.pipeline_duration.toFixed(1)}s</Text>
                                                        </HStack>
                                                    )}
                                                    {jobResults.dossier_updated && (
                                                        <HStack justify="space-between">
                                                            <Text>Dossier Updated:</Text>
                                                            <Badge colorScheme="green">YES</Badge>
                                                        </HStack>
                                                    )}

                                                    {/* Quality Metrics */}
                                                    {jobResults.quality_metrics && Object.keys(jobResults.quality_metrics).length > 0 && (
                                                        <Box>
                                                            <Text fontWeight="semibold" mb={2}>Quality Metrics:</Text>
                                                            <Code display="block" whiteSpace="pre-wrap" fontSize="xs" p={2}>
                                                                {JSON.stringify(jobResults.quality_metrics, null, 2)}
                                                            </Code>
                                                        </Box>
                                                    )}

                                                    {/* User Corrections Needed */}
                                                    {jobResults.user_corrections_needed && jobResults.user_corrections_needed.length > 0 && (
                                                        <Box>
                                                            <Text fontWeight="semibold" mb={2}>Corrections Needed:</Text>
                                                            <VStack align="stretch" spacing={1}>
                                                                {jobResults.user_corrections_needed.map((correction: string, index: number) => (
                                                                    <Badge key={index} colorScheme="orange" variant="outline">
                                                                        {correction}
                                                                    </Badge>
                                                                ))}
                                                            </VStack>
                                                        </Box>
                                                    )}
                                                </VStack>
                                            </AccordionPanel>
                                        </AccordionItem>
                                    </Accordion>
                                </>
                            )}
                        </VStack>
                    )}
                </ModalBody>
            </ModalContent>
        </Modal>
    );
};

const getStatusColor = (status: string) => {
    switch (status) {
        case 'completed': return 'green';
        case 'processing': return 'blue';
        case 'queued': return 'yellow';
        case 'pending': return 'gray';
        case 'failed': return 'red';
        case 'cancelled': return 'orange';
        case 'waiting_user': return 'purple';
        default: return 'gray';
    }
};

const getPriorityColor = (priority: string) => {
    switch (priority) {
        case 'critical': return 'red';
        case 'high': return 'orange';
        case 'normal': return 'blue';
        case 'low': return 'gray';
        case 'background': return 'gray';
        default: return 'gray';
    }
};

const getStatusIcon = (status: string) => {
    switch (status) {
        case 'completed': return FiCheck;
        case 'processing': return FiPlay;
        case 'queued': return FiClock;
        case 'pending': return FiPause;
        case 'failed': return FiAlertTriangle;
        case 'cancelled': return FiX;
        case 'waiting_user': return FiUser;
        default: return FiClock;
    }
};

const getJobTypeIcon = (jobType: string) => {
    switch (jobType) {
        case 'full_pipeline': return FiCpu;
        case 'person_analysis': return FiUser;
        case 'video_context': return FiVideo;
        case 'clothing_analysis': return FiShirt;
        default: return FiCpu;
    }
};

export const UC001JobList: React.FC<UC001JobListProps> = ({ onCancelJob }) => {
    const { jobs, fetchJobs, isLoading, subscribeToJobUpdates } = useUC001Dashboard();
    const { isOpen, onOpen, onClose } = useDisclosure();
    const [selectedJob, setSelectedJob] = useState<UC001Job | null>(null);
    const [filteredJobs, setFilteredJobs] = useState<UC001Job[]>([]);
    const [statusFilter, setStatusFilter] = useState<string>('all');
    const [searchTerm, setSearchTerm] = useState<string>('');

    const cardBg = useColorModeValue('white', 'gray.800');
    const borderColor = useColorModeValue('gray.200', 'gray.600');

    // Filter and search jobs
    useEffect(() => {
        let filtered = jobs;

        // Status filter
        if (statusFilter !== 'all') {
            filtered = filtered.filter(job => job.status === statusFilter);
        }

        // Search filter
        if (searchTerm) {
            filtered = filtered.filter(job =>
                job.job_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                job.user_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                job.job_type.toLowerCase().includes(searchTerm.toLowerCase())
            );
        }

        setFilteredJobs(filtered);
    }, [jobs, statusFilter, searchTerm]);

    const handleViewDetails = (job: UC001Job) => {
        setSelectedJob(job);
        onOpen();
    };

    const handleCancelJob = async (jobId: string) => {
        try {
            await onCancelJob(jobId);
            await fetchJobs(); // Refresh the job list
        } catch (error) {
            console.error('Failed to cancel job:', error);
        }
    };

    if (isLoading && jobs.length === 0) {
        return (
            <VStack spacing={4}>
                <Spinner />
                <Text>Loading jobs...</Text>
            </VStack>
        );
    }

    return (
        <VStack spacing={4} align="stretch">
            {/* Filters and Search */}
            <HStack spacing={4}>
                <InputGroup maxW="300px">
                    <InputLeftElement pointerEvents="none">
                        <Icon as={FiSearch} color="gray.400" />
                    </InputLeftElement>
                    <Input
                        placeholder="Search jobs..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </InputGroup>

                <Select
                    maxW="200px"
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    icon={<FiFilter />}
                >
                    <option value="all">All Status</option>
                    <option value="pending">Pending</option>
                    <option value="queued">Queued</option>
                    <option value="processing">Processing</option>
                    <option value="completed">Completed</option>
                    <option value="failed">Failed</option>
                    <option value="cancelled">Cancelled</option>
                    <option value="waiting_user">Waiting User</option>
                </Select>

                <Button
                    leftIcon={<FiRefreshCw />}
                    onClick={() => fetchJobs()}
                    size="sm"
                    isLoading={isLoading}
                >
                    Refresh
                </Button>
            </HStack>

            {/* Jobs Table */}
            {filteredJobs.length === 0 ? (
                <Alert status="info">
                    <AlertIcon />
                    No jobs found matching your criteria.
                </Alert>
            ) : (
                <TableContainer>
                    <Table variant="simple" size="sm">
                        <Thead>
                            <Tr>
                                <Th>Job ID</Th>
                                <Th>Type</Th>
                                <Th>Status</Th>
                                <Th>User</Th>
                                <Th>Priority</Th>
                                <Th>Progress</Th>
                                <Th>Created</Th>
                                <Th>Actions</Th>
                            </Tr>
                        </Thead>
                        <Tbody>
                            {filteredJobs.map((job) => (
                                <Tr key={job.job_id}>
                                    <Td>
                                        <Tooltip label={job.job_id}>
                                            <Code fontSize="xs">
                                                {job.job_id.slice(-8)}
                                            </Code>
                                        </Tooltip>
                                    </Td>
                                    <Td>
                                        <HStack spacing={2}>
                                            <Icon as={getJobTypeIcon(job.job_type)} />
                                            <Text fontSize="sm">
                                                {job.job_type.replace('_', ' ')}
                                            </Text>
                                        </HStack>
                                    </Td>
                                    <Td>
                                        <HStack spacing={2}>
                                            <Icon as={getStatusIcon(job.status)} />
                                            <Badge colorScheme={getStatusColor(job.status)}>
                                                {job.status}
                                            </Badge>
                                        </HStack>
                                    </Td>
                                    <Td>
                                        <Text fontSize="sm">{job.user_id}</Text>
                                    </Td>
                                    <Td>
                                        <Badge colorScheme={getPriorityColor(job.priority)} size="sm">
                                            {job.priority}
                                        </Badge>
                                    </Td>
                                    <Td>
                                        {job.progress !== undefined ? (
                                            <Box>
                                                <Progress
                                                    value={job.progress}
                                                    size="sm"
                                                    colorScheme="blue"
                                                    hasStripe={job.status === 'processing'}
                                                    isAnimated={job.status === 'processing'}
                                                />
                                                <Text fontSize="xs" color="gray.500">
                                                    {job.progress?.toFixed(0)}%
                                                </Text>
                                            </Box>
                                        ) : (
                                            <Text fontSize="sm" color="gray.500">-</Text>
                                        )}
                                    </Td>
                                    <Td>
                                        <Tooltip label={new Date(job.created_at).toLocaleString()}>
                                            <Text fontSize="xs" color="gray.500">
                                                {new Date(job.created_at).toLocaleDateString()}
                                            </Text>
                                        </Tooltip>
                                    </Td>
                                    <Td>
                                        <HStack spacing={1}>
                                            <Button
                                                size="xs"
                                                leftIcon={<FiEye />}
                                                onClick={() => handleViewDetails(job)}
                                            >
                                                View
                                            </Button>
                                            {(job.status === 'pending' || job.status === 'queued' || job.status === 'processing') && (
                                                <Button
                                                    size="xs"
                                                    colorScheme="red"
                                                    variant="outline"
                                                    leftIcon={<FiX />}
                                                    onClick={() => handleCancelJob(job.job_id)}
                                                >
                                                    Cancel
                                                </Button>
                                            )}
                                        </HStack>
                                    </Td>
                                </Tr>
                            ))}
                        </Tbody>
                    </Table>
                </TableContainer>
            )}

            {/* Job Details Modal */}
            <JobDetailsModal
                isOpen={isOpen}
                onClose={onClose}
                job={selectedJob}
            />
        </VStack>
    );
};
