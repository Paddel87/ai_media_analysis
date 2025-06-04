/**
 * UC-001 Enhanced Manual Analysis - API Client
 * Version: 1.0.0 - HTTP Client for UC-001 Job Manager Integration
 * Status: ALPHA 0.6.0 - Power-User-First Strategy
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

// UC-001 API Configuration
const UC001_API_BASE_URL = process.env.REACT_APP_UC001_API_URL || 'http://localhost:8012';

// Create dedicated UC-001 API client
export const uc001ApiClient: AxiosInstance = axios.create({
  baseURL: UC001_API_BASE_URL,
  timeout: 30000, // 30 second timeout for pipeline operations
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-UC001-Client': 'Web-Interface-v1.0.0',
    'X-Power-User-Mode': 'true',
    'X-Research-Mode': 'true'
  }
});

// Request interceptor for UC-001 specific headers
uc001ApiClient.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    // Add timestamp for debugging
    config.headers = {
      ...config.headers,
      'X-Request-Timestamp': new Date().toISOString(),
      'X-UC001-Session': `session_${Date.now()}`
    };

    // Log UC-001 API requests in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`🎯 UC-001 API Request: ${config.method?.toUpperCase()} ${config.url}`, {
        data: config.data,
        params: config.params
      });
    }

    return config;
  },
  (error) => {
    console.error('❌ UC-001 API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for UC-001 specific error handling
uc001ApiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // Log successful UC-001 API responses in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`✅ UC-001 API Response: ${response.config.method?.toUpperCase()} ${response.config.url}`, {
        status: response.status,
        data: response.data
      });
    }

    return response;
  },
  (error) => {
    // Enhanced error handling for UC-001 specific errors
    if (error.response) {
      const { status, data } = error.response;

      // Handle specific UC-001 error scenarios
      switch (status) {
        case 404:
          if (error.config.url?.includes('/jobs/')) {
            error.message = 'UC-001 job not found. It may have been completed or cancelled.';
          } else {
            error.message = 'UC-001 endpoint not found. Please check the service status.';
          }
          break;

        case 503:
          error.message = 'UC-001 pipeline services are unavailable. Please try again later.';
          break;

        case 429:
          error.message = 'UC-001 pipeline is at capacity. Please wait before submitting more jobs.';
          break;

        case 422:
          error.message = data?.detail || 'Invalid job submission data. Please check your input.';
          break;

        case 500:
          error.message = 'UC-001 pipeline internal error. Please contact support.';
          break;

        default:
          error.message = data?.detail || `UC-001 API error (${status})`;
      }
    } else if (error.request) {
      error.message = 'Cannot connect to UC-001 pipeline services. Please check your connection.';
    } else {
      error.message = error.message || 'UC-001 API request failed';
    }

    console.error('❌ UC-001 API Error:', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      message: error.message,
      data: error.response?.data
    });

    return Promise.reject(error);
  }
);

// UC-001 Specific API Methods
export const uc001Api = {
  // Pipeline Status & Health
  async getPipelineStatus() {
    return uc001ApiClient.get('/uc001/pipeline/status');
  },

  async getPipelineMetrics() {
    return uc001ApiClient.get('/uc001/pipeline/metrics');
  },

  async getHealthStatus() {
    return uc001ApiClient.get('/health/uc001');
  },

  // Job Management
  async submitJob(jobData: any) {
    return uc001ApiClient.post('/uc001/jobs/submit', jobData);
  },

  async getJobStatus(jobId: string) {
    return uc001ApiClient.get(`/uc001/jobs/${jobId}/status`);
  },

  async getJobResults(jobId: string) {
    return uc001ApiClient.get(`/uc001/jobs/${jobId}/results`);
  },

  async cancelJob(jobId: string) {
    return uc001ApiClient.post(`/uc001/jobs/${jobId}/cancel`);
  },

  async listJobs(params?: { status?: string; user_id?: string; limit?: number }) {
    return uc001ApiClient.get('/uc001/jobs', { params });
  },

  // Convenience Analysis Endpoints
  async submitFullAnalysis(mediaPath: string, userId: string, personId?: string, priority = 'normal') {
    return uc001ApiClient.post('/uc001/analyze/full', {
      media_path: mediaPath,
      user_id: userId,
      person_id: personId,
      priority
    });
  },

  async submitPersonAnalysis(mediaPath: string, userId: string, personId?: string) {
    return uc001ApiClient.post('/uc001/analyze/person', {
      media_path: mediaPath,
      user_id: userId,
      person_id: personId
    });
  },

  async submitClothingAnalysis(mediaPath: string, userId: string, personId?: string) {
    return uc001ApiClient.post('/uc001/analyze/clothing', {
      media_path: mediaPath,
      user_id: userId,
      person_id: personId
    });
  },

  // Development & Debugging
  async validateServices() {
    return uc001ApiClient.get('/uc001/debug/services');
  },

  async getQueueDebugInfo() {
    return uc001ApiClient.get('/uc001/debug/queue');
  },

  // Real-time Job Monitoring
  createJobStatusStream(jobId: string, callback: (status: any) => void) {
    const pollInterval = setInterval(async () => {
      try {
        const response = await this.getJobStatus(jobId);
        callback(response.data);

        // Stop polling if job is in terminal state
        const terminalStates = ['completed', 'failed', 'cancelled'];
        if (terminalStates.includes(response.data.status)) {
          clearInterval(pollInterval);
        }
      } catch (error) {
        console.error(`Failed to poll job status for ${jobId}:`, error);
      }
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(pollInterval);
  }
};

// Export default client for general use
export default uc001ApiClient;
