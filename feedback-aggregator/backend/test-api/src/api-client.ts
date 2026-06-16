import axios, { AxiosInstance, AxiosResponse } from 'axios';
import FormData from 'form-data';
import * as fs from 'fs';
import { config, API_ROUTES } from './config';
import {
  HealthResponse,
  UploadMainFileResponse,
  ClearMainFileResponse,
  ProcessResponse,
  GetDataResponse
} from './types';

/**
 * Client API pour communiquer avec le backend Flask
 */
export class ApiClient {
  private client: AxiosInstance;

  constructor(baseUrl: string = config.baseUrl) {
    this.client = axios.create({
      baseURL: baseUrl,
      timeout: config.timeout,
      headers: {
        'Accept': 'application/json'
      }
    });
  }

  /**
   * GET /api/health
   */
  async health(): Promise<AxiosResponse<HealthResponse>> {
    return this.client.get<HealthResponse>(API_ROUTES.health);
  }

  /**
   * POST /api/upload-main-file
   */
  async uploadMainFile(
    filePath: string,
    sheetName?: string
  ): Promise<AxiosResponse<UploadMainFileResponse>> {
    const formData = new FormData();
    formData.append('file', fs.createReadStream(filePath));
    
    if (sheetName) {
      formData.append('sheet_name', sheetName);
    }

    return this.client.post<UploadMainFileResponse>(
      API_ROUTES.uploadMainFile,
      formData,
      {
        headers: formData.getHeaders()
      }
    );
  }

  /**
   * DELETE /api/clear-main-file
   */
  async clearMainFile(): Promise<AxiosResponse<ClearMainFileResponse>> {
    return this.client.delete<ClearMainFileResponse>(API_ROUTES.clearMainFile);
  }

  /**
   * POST /api/process-celldown
   */
  async processCelldown(
    targetFilePath: string,
    params: {
      reference_name?: string;
      reference_date?: string;
      date_str: string; // REQUIS format: jjmmaaaa
      colown_key_path_source?: string;
      target_key_column?: string;
      target_value_column?: string;
      source_sheet_path?: string;
      start_column?: string;
    }
  ): Promise<AxiosResponse<ProcessResponse>> {
    const formData = new FormData();
    formData.append('file', fs.createReadStream(targetFilePath));
    
    // Ajouter tous les paramètres
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        formData.append(key, value);
      }
    });

    return this.client.post<ProcessResponse>(
      API_ROUTES.processCelldown,
      formData,
      {
        headers: formData.getHeaders()
      }
    );
  }

  /**
   * POST /api/process-xlookup
   */
  async processXlookup(
    targetFilePath: string,
    params: {
      source_key_column?: string;
      target_key_column?: string;
      target_value_column?: string;
      source_sheet_name?: string;
      target_sheet_name?: string;
      result_column_name?: string;
      reference_name?: string;
      reference_date?: string;
      result_position_column?: string;
    } = {}
  ): Promise<AxiosResponse<ProcessResponse>> {
    const formData = new FormData();
    formData.append('file', fs.createReadStream(targetFilePath));
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        formData.append(key, value);
      }
    });

    return this.client.post<ProcessResponse>(
      API_ROUTES.processXlookup,
      formData,
      {
        headers: formData.getHeaders()
      }
    );
  }

  /**
   * POST /api/process-ticket
   */
  async processTicket(
    targetFilePath: string,
    params: {
      reference_name?: string;
      reference_date?: string;
      source_key_column?: string;
      target_key_column?: string;
      source_sheet_name?: string;
      target_sheet_name?: string;
      result_column_name?: string;
      target_join_columns?: string; // JSON string
      join_separator?: string;
      ignore_empty?: string; // "true" ou "false"
      extract_source_column?: string; // JSON string
    } = {}
  ): Promise<AxiosResponse<ProcessResponse>> {
    const formData = new FormData();
    formData.append('file', fs.createReadStream(targetFilePath));
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        formData.append(key, value);
      }
    });

    return this.client.post<ProcessResponse>(
      API_ROUTES.processTicket,
      formData,
      {
        headers: formData.getHeaders()
      }
    );
  }

  /**
   * GET /api/get-data
   */
  async getData(params: {
    sheet?: string;
    limit?: number;
    offset?: number;
  } = {}): Promise<AxiosResponse<GetDataResponse>> {
    return this.client.get<GetDataResponse>(API_ROUTES.getData, { params });
  }

  /**
   * GET /api/export
   */
  async export(): Promise<AxiosResponse<Buffer>> {
    return this.client.get<Buffer>(API_ROUTES.export, {
      responseType: 'arraybuffer'
    });
  }
}
