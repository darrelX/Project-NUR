import { TestConfig } from './types';
import * as path from 'path';

export const config: TestConfig = {
  baseUrl: 'http://localhost:5000',
  timeout: 60000,
  testFilesDir: path.resolve(__dirname, '../../test_files')
};

export const API_ROUTES = {
  health: '/api/health',
  uploadMainFile: '/api/upload-main-file',
  clearMainFile: '/api/clear-main-file',
  processCelldown: '/api/process-celldown',
  processXlookup: '/api/process-xlookup',
  processTicket: '/api/process-ticket',
  getData: '/api/get-data',
  export: '/api/export'
} as const;
