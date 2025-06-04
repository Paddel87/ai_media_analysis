/**
 * UC-001 Enhanced Manual Analysis - Dashboard Hook
 * Version: 1.0.0 - State Management & API Integration
 * Status: ALPHA 0.6.0 - Power-User-First Strategy
 */

import { useToast } from '@chakra-ui/react';
import { useCallback, useEffect, useState } from 'react';
import { uc001ApiClient } from '../services/uc001ApiClient';

// Types
export interface UC001Job {
  job_id: string;
  status: string;
  job_type: string;
  media_path: string;
  user_id: string;
  progress?: number;
  created_at: string;
  updated_at?: string;
  current_step?: string;
  error_message?: string;
  priority: string;
  research_mode: boolean;
}

export interface UC001Metrics {
  total_jobs_processed: number;
  completed_jobs: number;
  failed_jobs: number;
  success_rate: number;
  average_pipeline_duration: number;
  active_jobs: number;
  queue_size: number;
  timestamp: string;
}

export interface UC001PipelineStatus {
  pipeline_status: string;
  services: Record<string, any>;
  active_jobs: number;
  queue_size: number;
  max_concurrent: number;
  research_mode: boolean;
  power_user_mode: boolean;
  timestamp: string;
  active_jobs_by_status: Record<string, number>;
  service_endpoints: Record<string, any>;
}

export interface UC001JobSubmission {
  job_type: 'full_pipeline' | 'person_analysis' | 'video_context' | 'clothing_analysis';
  media_path: string;
  person_id?: string;
  user_id: string;
  priority?: 'critical' | 'high' | 'normal' | 'low' | 'background';
  analysis_config?: Record<string, any>;
  create_dossier?: boolean;
  update_existing?: boolean;
  enable_clothing_analysis?: boolean;
  enable_video_context?: boolean;
  enable_corrections?: boolean;
  research_mode?: boolean;
}

export const useUC001Dashboard = () => {
  // State
  const [pipelineStatus, setPipelineStatus] = useState<UC001PipelineStatus | null>(null);
  const [metrics, setMetrics] = useState<UC001Metrics | null>(null);
  const [jobs, setJobs] = useState<UC001Job[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const toast = useToast();

  // Fetch pipeline status
  const fetchPipelineStatus = useCallback(async () => {
    try {
      const response = await uc001ApiClient.get('/uc001/pipeline/status');
      setPipelineStatus(response.data);
      setError(null);
    } catch (err: any) {
      console.error('Failed to fetch pipeline status:', err);
      setError(err.message || 'Failed to fetch pipeline status');
    }
  }, []);

  // Fetch metrics
  const fetchMetrics = useCallback(async () => {
    try {
      const response = await uc001ApiClient.get('/uc001/pipeline/metrics');
      setMetrics(response.data);
      setError(null);
    } catch (err: any) {
      console.error('Failed to fetch metrics:', err);
      setError(err.message || 'Failed to fetch metrics');
    }
  }, []);

  // Fetch jobs list
  const fetchJobs = useCallback(async (limit = 50) => {
    try {
      const response = await uc001ApiClient.get(`/uc001/jobs?limit=${limit}`);
      setJobs(response.data.jobs || []);
      setError(null);
    } catch (err: any) {
      console.error('Failed to fetch jobs:', err);
      setError(err.message || 'Failed to fetch jobs');
    }
  }, []);

  // Refresh all data
  const refreshData = useCallback(async () => {
    setIsLoading(true);
    try {
      await Promise.all([
        fetchPipelineStatus(),
        fetchMetrics(),
        fetchJobs()
      ]);
    } catch (err) {
      console.error('Failed to refresh data:', err);
    } finally {
      setIsLoading(false);
    }
  }, [fetchPipelineStatus, fetchMetrics, fetchJobs]);

  // Submit new UC-001 job
  const submitJob = useCallback(async (jobData: UC001JobSubmission) => {
    try {
      setIsLoading(true);

      const response = await uc001ApiClient.post('/uc001/jobs/submit', {
        job_type: jobData.job_type,
        media_path: jobData.media_path,
        person_id: jobData.person_id,
        user_id: jobData.user_id,
        priority: jobData.priority || 'normal',
        analysis_config: jobData.analysis_config || {},
        create_dossier: jobData.create_dossier !== false,
        update_existing: jobData.update_existing !== false,
        enable_clothing_analysis: jobData.enable_clothing_analysis !== false,
        enable_video_context: jobData.enable_video_context !== false,
        enable_corrections: jobData.enable_corrections !== false,
        research_mode: jobData.research_mode !== false
      });

      toast({
        title: 'Job Submitted Successfully',
        description: `UC-001 job ${response.data.job_id} has been submitted for processing`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });

      // Refresh data after submission
      await refreshData();

      return response.data.job_id;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to submit job';

      toast({
        title: 'Job Submission Failed',
        description: errorMessage,
        status: 'error',
        duration: 8000,
        isClosable: true,
      });

      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [toast, refreshData]);

  // Cancel UC-001 job
  const cancelJob = useCallback(async (jobId: string) => {
    try {
      await uc001ApiClient.post(`/uc001/jobs/${jobId}/cancel`);

      toast({
        title: 'Job Cancelled',
        description: `Job ${jobId} has been cancelled successfully`,
        status: 'info',
        duration: 3000,
        isClosable: true,
      });

      // Refresh jobs list
      await fetchJobs();
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to cancel job';

      toast({
        title: 'Job Cancellation Failed',
        description: errorMessage,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });

      throw new Error(errorMessage);
    }
  }, [toast, fetchJobs]);

  // Get job details
  const getJobDetails = useCallback(async (jobId: string) => {
    try {
      const response = await uc001ApiClient.get(`/uc001/jobs/${jobId}/status`);
      return response.data;
    } catch (err: any) {
      console.error(`Failed to fetch job details for ${jobId}:`, err);
      throw new Error(err.response?.data?.detail || err.message || 'Failed to fetch job details');
    }
  }, []);

  // Get job results
  const getJobResults = useCallback(async (jobId: string) => {
    try {
      const response = await uc001ApiClient.get(`/uc001/jobs/${jobId}/results`);
      return response.data;
    } catch (err: any) {
      console.error(`Failed to fetch job results for ${jobId}:`, err);
      throw new Error(err.response?.data?.detail || err.message || 'Failed to fetch job results');
    }
  }, []);

  // Check service health
  const checkServiceHealth = useCallback(async () => {
    try {
      const response = await uc001ApiClient.get('/health/uc001');
      return response.data;
    } catch (err: any) {
      console.error('Failed to check service health:', err);
      throw new Error(err.message || 'Failed to check service health');
    }
  }, []);

  // Validate services
  const validateServices = useCallback(async () => {
    try {
      const response = await uc001ApiClient.get('/uc001/debug/services');
      return response.data;
    } catch (err: any) {
      console.error('Failed to validate services:', err);
      throw new Error(err.message || 'Failed to validate services');
    }
  }, []);

  // Get queue debug info
  const getQueueDebugInfo = useCallback(async () => {
    try {
      const response = await uc001ApiClient.get('/uc001/debug/queue');
      return response.data;
    } catch (err: any) {
      console.error('Failed to get queue debug info:', err);
      throw new Error(err.message || 'Failed to get queue debug info');
    }
  }, []);

  // Auto-refresh on mount
  useEffect(() => {
    refreshData();
  }, [refreshData]);

  // Real-time job status updates
  const subscribeToJobUpdates = useCallback((jobId: string, callback: (status: any) => void) => {
    const interval = setInterval(async () => {
      try {
        const status = await getJobDetails(jobId);
        callback(status);

        // Stop polling if job is completed or failed
        if (status.status === 'completed' || status.status === 'failed' || status.status === 'cancelled') {
          clearInterval(interval);
        }
      } catch (err) {
        console.error(`Failed to fetch job status for ${jobId}:`, err);
      }
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(interval);
  }, [getJobDetails]);

  return {
    // State
    pipelineStatus,
    metrics,
    jobs,
    isLoading,
    error,

    // Actions
    refreshData,
    submitJob,
    cancelJob,
    getJobDetails,
    getJobResults,
    fetchJobs,

    // Utility functions
    checkServiceHealth,
    validateServices,
    getQueueDebugInfo,
    subscribeToJobUpdates,

    // Computed values
    isHealthy: pipelineStatus?.pipeline_status === 'healthy',
    activeJobsCount: pipelineStatus?.active_jobs || 0,
    queueSize: pipelineStatus?.queue_size || 0,
    isResearchMode: pipelineStatus?.research_mode || false,
    isPowerUserMode: pipelineStatus?.power_user_mode || false,
    serviceCount: pipelineStatus?.services ? Object.keys(pipelineStatus.services).length : 0,
    healthyServiceCount: pipelineStatus?.services
      ? Object.values(pipelineStatus.services).filter((service: any) => service.status === 'healthy').length
      : 0
  };
};
