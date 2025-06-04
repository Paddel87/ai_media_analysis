/**
 * UC-001 Enhanced Manual Analysis - Analysis Form Component
 * Version: 1.0.0 - Job Submission Interface for Enhanced Manual Analysis
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
    Divider,
    FormControl,
    FormErrorMessage,
    FormHelperText,
    FormLabel,
    HStack,
    Icon,
    Input,
    Select,
    Switch,
    Text,
    Textarea,
    useColorModeValue,
    VStack
} from '@chakra-ui/react';
import React, { useState } from 'react';
import {
    FiCpu,
    FiEye,
    FiSettings,
    FiShirt,
    FiTarget,
    FiUpload,
    FiUser,
    FiVideo,
    FiZap
} from 'react-icons/fi';
import { UC001JobSubmission } from '../hooks/useUC001Dashboard';

interface UC001AnalysisFormProps {
    onSubmit: (jobData: UC001JobSubmission) => Promise<string>;
    isLoading?: boolean;
}

export const UC001AnalysisForm: React.FC<UC001AnalysisFormProps> = ({
    onSubmit,
    isLoading = false
}) => {
    const [formData, setFormData] = useState<UC001JobSubmission>({
        job_type: 'full_pipeline',
        media_path: '',
        user_id: '',
        person_id: '',
        priority: 'normal',
        analysis_config: {},
        create_dossier: true,
        update_existing: true,
        enable_clothing_analysis: true,
        enable_video_context: true,
        enable_corrections: true,
        research_mode: true
    });

    const [errors, setErrors] = useState<Record<string, string>>({});
    const [submitError, setSubmitError] = useState<string>('');

    const cardBg = useColorModeValue('gray.50', 'gray.700');
    const borderColor = useColorModeValue('gray.200', 'gray.600');

    // Validation
    const validateForm = (): boolean => {
        const newErrors: Record<string, string> = {};

        if (!formData.media_path.trim()) {
            newErrors.media_path = 'Media path is required';
        }

        if (!formData.user_id.trim()) {
            newErrors.user_id = 'User ID is required';
        }

        // Validate media path format (basic check)
        if (formData.media_path && !formData.media_path.match(/\.(jpg|jpeg|png|mp4|avi|mov)$/i)) {
            newErrors.media_path = 'Please provide a valid media file path (.jpg, .png, .mp4, etc.)';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    // Handle form submission
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSubmitError('');

        if (!validateForm()) {
            return;
        }

        try {
            await onSubmit(formData);

            // Reset form on successful submission
            setFormData({
                ...formData,
                media_path: '',
                person_id: ''
            });
        } catch (error: any) {
            setSubmitError(error.message || 'Failed to submit analysis job');
        }
    };

    // Update form data
    const updateFormData = (field: keyof UC001JobSubmission, value: any) => {
        setFormData(prev => ({
            ...prev,
            [field]: value
        }));

        // Clear error when field is updated
        if (errors[field]) {
            setErrors(prev => ({
                ...prev,
                [field]: ''
            }));
        }
    };

    const getJobTypeDescription = (jobType: string) => {
        switch (jobType) {
            case 'full_pipeline':
                return 'Complete analysis including person detection, video context, and clothing analysis';
            case 'person_analysis':
                return 'Person detection and dossier management only';
            case 'video_context':
                return 'Video context analysis with LLM processing';
            case 'clothing_analysis':
                return 'Clothing classification with 200+ categories';
            default:
                return '';
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

    return (
        <Box as="form" onSubmit={handleSubmit}>
            <VStack spacing={6} align="stretch">
                {/* Submit Error */}
                {submitError && (
                    <Alert status="error">
                        <AlertIcon />
                        {submitError}
                    </Alert>
                )}

                {/* Basic Job Configuration */}
                <VStack spacing={4} align="stretch">
                    <Text fontWeight="bold" fontSize="md" color="blue.500">
                        <Icon as={FiTarget} mr={2} />
                        Job Configuration
                    </Text>

                    {/* Job Type */}
                    <FormControl isInvalid={!!errors.job_type}>
                        <FormLabel>Analysis Type</FormLabel>
                        <Select
                            value={formData.job_type}
                            onChange={(e) => updateFormData('job_type', e.target.value as any)}
                        >
                            <option value="full_pipeline">🔬 Full Pipeline (Complete Analysis)</option>
                            <option value="person_analysis">👤 Person Analysis Only</option>
                            <option value="video_context">🎥 Video Context Only</option>
                            <option value="clothing_analysis">👕 Clothing Analysis Only</option>
                        </Select>
                        <FormHelperText>
                            {getJobTypeDescription(formData.job_type)}
                        </FormHelperText>
                        <FormErrorMessage>{errors.job_type}</FormErrorMessage>
                    </FormControl>

                    {/* Media Path */}
                    <FormControl isRequired isInvalid={!!errors.media_path}>
                        <FormLabel>Media File Path</FormLabel>
                        <Input
                            placeholder="/app/data/media/video.mp4 or /app/data/frames/image.jpg"
                            value={formData.media_path}
                            onChange={(e) => updateFormData('media_path', e.target.value)}
                        />
                        <FormHelperText>
                            Full path to the media file (image or video) within the container
                        </FormHelperText>
                        <FormErrorMessage>{errors.media_path}</FormErrorMessage>
                    </FormControl>

                    {/* User ID */}
                    <FormControl isRequired isInvalid={!!errors.user_id}>
                        <FormLabel>User ID</FormLabel>
                        <Input
                            placeholder="researcher_001 or analyst_name"
                            value={formData.user_id}
                            onChange={(e) => updateFormData('user_id', e.target.value)}
                        />
                        <FormHelperText>
                            Identifier for the user submitting this analysis
                        </FormHelperText>
                        <FormErrorMessage>{errors.user_id}</FormErrorMessage>
                    </FormControl>

                    {/* Person ID (Optional) */}
                    <FormControl>
                        <FormLabel>Person ID (Optional)</FormLabel>
                        <Input
                            placeholder="existing_person_123"
                            value={formData.person_id || ''}
                            onChange={(e) => updateFormData('person_id', e.target.value || undefined)}
                        />
                        <FormHelperText>
                            Link to existing person in dossier system (leave blank for new person)
                        </FormHelperText>
                    </FormControl>

                    {/* Priority */}
                    <FormControl>
                        <FormLabel>Priority Level</FormLabel>
                        <HStack>
                            <Select
                                value={formData.priority}
                                onChange={(e) => updateFormData('priority', e.target.value)}
                                maxW="200px"
                            >
                                <option value="critical">Critical</option>
                                <option value="high">High</option>
                                <option value="normal">Normal</option>
                                <option value="low">Low</option>
                                <option value="background">Background</option>
                            </Select>
                            <Badge colorScheme={getPriorityColor(formData.priority!)}>
                                {formData.priority?.toUpperCase()}
                            </Badge>
                        </HStack>
                        <FormHelperText>
                            Higher priority jobs are processed first
                        </FormHelperText>
                    </FormControl>
                </VStack>

                <Divider />

                {/* Advanced Configuration */}
                <Accordion allowToggle>
                    <AccordionItem>
                        <AccordionButton>
                            <Box flex="1" textAlign="left">
                                <Text fontWeight="bold" fontSize="md" color="purple.500">
                                    <Icon as={FiSettings} mr={2} />
                                    Advanced Pipeline Configuration
                                </Text>
                            </Box>
                            <AccordionIcon />
                        </AccordionButton>
                        <AccordionPanel pb={4}>
                            <VStack spacing={4} align="stretch">
                                {/* Pipeline Feature Toggles */}
                                <Text fontWeight="semibold" fontSize="sm" color="gray.600">
                                    Pipeline Features
                                </Text>

                                <VStack spacing={3} align="stretch" bg={cardBg} p={4} borderRadius="md">
                                    <HStack justify="space-between">
                                        <HStack>
                                            <Icon as={FiUser} color="blue.500" />
                                            <Text>Create/Update Dossier</Text>
                                        </HStack>
                                        <Switch
                                            isChecked={formData.create_dossier}
                                            onChange={(e) => updateFormData('create_dossier', e.target.checked)}
                                        />
                                    </HStack>

                                    <HStack justify="space-between">
                                        <HStack>
                                            <Icon as={FiShirt} color="green.500" />
                                            <Text>Enable Clothing Analysis</Text>
                                        </HStack>
                                        <Switch
                                            isChecked={formData.enable_clothing_analysis}
                                            onChange={(e) => updateFormData('enable_clothing_analysis', e.target.checked)}
                                        />
                                    </HStack>

                                    <HStack justify="space-between">
                                        <HStack>
                                            <Icon as={FiVideo} color="purple.500" />
                                            <Text>Enable Video Context</Text>
                                        </HStack>
                                        <Switch
                                            isChecked={formData.enable_video_context}
                                            onChange={(e) => updateFormData('enable_video_context', e.target.checked)}
                                        />
                                    </HStack>

                                    <HStack justify="space-between">
                                        <HStack>
                                            <Icon as={FiEye} color="orange.500" />
                                            <Text>Enable User Corrections</Text>
                                        </HStack>
                                        <Switch
                                            isChecked={formData.enable_corrections}
                                            onChange={(e) => updateFormData('enable_corrections', e.target.checked)}
                                        />
                                    </HStack>
                                </VStack>

                                {/* Power User Features */}
                                <Text fontWeight="semibold" fontSize="sm" color="gray.600">
                                    Power User Features
                                </Text>

                                <VStack spacing={3} align="stretch" bg={cardBg} p={4} borderRadius="md">
                                    <HStack justify="space-between">
                                        <HStack>
                                            <Icon as={FiZap} color="purple.500" />
                                            <Text>Research Mode</Text>
                                        </HStack>
                                        <Switch
                                            isChecked={formData.research_mode}
                                            onChange={(e) => updateFormData('research_mode', e.target.checked)}
                                        />
                                    </HStack>

                                    <HStack justify="space-between">
                                        <HStack>
                                            <Icon as={FiCpu} color="blue.500" />
                                            <Text>Update Existing Records</Text>
                                        </HStack>
                                        <Switch
                                            isChecked={formData.update_existing}
                                            onChange={(e) => updateFormData('update_existing', e.target.checked)}
                                        />
                                    </HStack>
                                </VStack>

                                {/* Analysis Configuration */}
                                <FormControl>
                                    <FormLabel>Custom Analysis Configuration (JSON)</FormLabel>
                                    <Textarea
                                        placeholder='{"confidence_threshold": 0.8, "custom_categories": ["formal", "casual"]}'
                                        value={JSON.stringify(formData.analysis_config, null, 2)}
                                        onChange={(e) => {
                                            try {
                                                const config = JSON.parse(e.target.value || '{}');
                                                updateFormData('analysis_config', config);
                                            } catch (error) {
                                                // Keep typing, don't update if invalid JSON
                                            }
                                        }}
                                        rows={4}
                                        fontFamily="mono"
                                        fontSize="sm"
                                    />
                                    <FormHelperText>
                                        Optional custom configuration in JSON format
                                    </FormHelperText>
                                </FormControl>
                            </VStack>
                        </AccordionPanel>
                    </AccordionItem>
                </Accordion>

                {/* Submit Button */}
                <Button
                    type="submit"
                    colorScheme="blue"
                    size="lg"
                    leftIcon={<FiUpload />}
                    isLoading={isLoading}
                    loadingText="Submitting Analysis Job..."
                    isDisabled={!formData.media_path || !formData.user_id}
                >
                    Submit UC-001 Analysis Job
                </Button>

                {/* Job Summary */}
                <Box bg={cardBg} p={4} borderRadius="md" border="1px" borderColor={borderColor}>
                    <Text fontWeight="bold" mb={2}>Job Summary:</Text>
                    <VStack align="start" spacing={1} fontSize="sm">
                        <Text>🔬 Type: {formData.job_type.replace('_', ' ').toUpperCase()}</Text>
                        <Text>⚡ Priority: {formData.priority?.toUpperCase()}</Text>
                        <Text>🎯 Features: {[
                            formData.enable_clothing_analysis && 'Clothing',
                            formData.enable_video_context && 'Video Context',
                            formData.enable_corrections && 'User Corrections'
                        ].filter(Boolean).join(', ') || 'Basic Analysis'}</Text>
                        <Text>🧪 Research Mode: {formData.research_mode ? 'ENABLED' : 'DISABLED'}</Text>
                    </VStack>
                </Box>
            </VStack>
        </Box>
    );
};
