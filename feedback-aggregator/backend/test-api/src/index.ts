/**
 * Index principal - Exports publics du package
 */

// Client API
export { ApiClient } from './api-client';

// Types
export type {
  HealthResponse,
  UploadMainFileResponse,
  ClearMainFileResponse,
  ProcessResponse,
  GetDataResponse,
  ErrorResponse,
  TestResult,
  TestConfig
} from './types';

// Configuration
export { config, API_ROUTES } from './config';

// Utilitaires
export {
  colors,
  displayTestResult,
  displaySectionHeader,
  displaySummary,
  fileExists,
  readFile,
  listFiles,
  sleep,
  measureTime
} from './utils';

// Exemples
export { examples, advancedExample } from './examples';
