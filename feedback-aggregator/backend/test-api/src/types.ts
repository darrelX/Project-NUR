/**
 * Types pour les réponses de l'API
 */

export interface HealthResponse {
  status: string;
  message: string;
}

export interface UploadMainFileResponse {
  success: boolean;
  filename: string;
  sheet_name?: string;
  path: string;
  lines: number;
  size: number;
}

export interface ClearMainFileResponse {
  success: boolean;
  message: string;
}

export interface ProcessResponse {
  success: boolean;
  message: string;
  filename: string;
  lines: number;
  columns: string[];
  data: any[];
}

export interface GetDataResponse {
  success: boolean;
  total_lines: number;
  offset: number;
  limit: number;
  columns: string[];
  data: any[];
}

export interface ErrorResponse {
  error: string;
}

export interface TestResult {
  route: string;
  method: string;
  success: boolean;
  statusCode: number;
  duration: number;
  message: string;
  data?: any;
  error?: string;
}

export interface TestConfig {
  baseUrl: string;
  timeout: number;
  testFilesDir: string;
}
