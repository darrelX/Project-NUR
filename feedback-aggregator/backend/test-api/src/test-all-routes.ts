import * as path from 'path';
import { ApiClient } from './api-client';
import { config } from './config';
import { TestResult } from './types';
import {
  displaySectionHeader,
  displayTestResult,
  displaySummary,
  fileExists,
  measureTime,
  sleep
} from './utils';

/**
 * Script principal pour tester toutes les routes de l'API
 */
class ApiTester {
  private client: ApiClient;
  private results: TestResult[] = [];
  private mainFilePath: string;
  private targetCelldownPath: string;
  private targetXlookupPath: string;
  private targetTicketPath: string;

  constructor() {
    this.client = new ApiClient(config.baseUrl);
    this.mainFilePath = path.join(config.testFilesDir, 'main_test.xlsx');
    this.targetCelldownPath = path.join(config.testFilesDir, 'target_ticket.xlsx');
    this.targetXlookupPath = path.join(config.testFilesDir, 'target_xlookup.xlsx');
    this.targetTicketPath = path.join(config.testFilesDir, 'target_ticket.xlsx');
  }

  /**
   * Vérifie les prérequis
   */
  private checkPrerequisites(): boolean {
    displaySectionHeader('VÉRIFICATION DES PRÉREQUIS');

    const files = [
      { name: 'Fichier principal', path: this.mainFilePath },
      { name: 'Fichier target (celldown)', path: this.targetCelldownPath },
      { name: 'Fichier target (xlookup)', path: this.targetXlookupPath },
      { name: 'Fichier target (ticket)', path: this.targetTicketPath }
    ];

    let allExist = true;
    for (const file of files) {
      const exists = fileExists(file.path);
      console.log(`${exists ? '✅' : '❌'} ${file.name}: ${file.path}`);
      if (!exists) {
        allExist = false;
      }
    }

    if (!allExist) {
      console.log('\n⚠️  Créez les fichiers de test manquants dans backend/test_files/');
      return false;
    }

    return true;
  }

  /**
   * Test 1: GET /api/health
   */
  private async testHealth(): Promise<void> {
    try {
      const { result: response, duration } = await measureTime(() =>
        this.client.health()
      );

      this.results.push({
        route: '/api/health',
        method: 'GET',
        success: response.status === 200,
        statusCode: response.status,
        duration,
        message: response.data.message,
        data: response.data
      });
    } catch (error: any) {
      this.results.push({
        route: '/api/health',
        method: 'GET',
        success: false,
        statusCode: error.response?.status || 0,
        duration: 0,
        message: 'Serveur non accessible',
        error: error.message
      });
    }
  }

  /**
   * Test 2: POST /api/upload-main-file
   */
  private async testUploadMainFile(): Promise<void> {
    try {
      const { result: response, duration } = await measureTime(() =>
        this.client.uploadMainFile(this.mainFilePath)
      );

      this.results.push({
        route: '/api/upload-main-file',
        method: 'POST',
        success: response.status === 200 && response.data.success,
        statusCode: response.status,
        duration,
        message: `Fichier uploadé: ${response.data.filename} (${response.data.lines} lignes)`,
        data: { filename: response.data.filename, lines: response.data.lines }
      });
    } catch (error: any) {
      this.results.push({
        route: '/api/upload-main-file',
        method: 'POST',
        success: false,
        statusCode: error.response?.status || 0,
        duration: 0,
        message: 'Échec de l\'upload',
        error: error.response?.data?.error || error.message
      });
    }
  }

  /**
   * Test 3: GET /api/get-data
   */
  private async testGetData(): Promise<void> {
    try {
      const { result: response, duration } = await measureTime(() =>
        this.client.getData({ limit: 10 })
      );

      this.results.push({
        route: '/api/get-data',
        method: 'GET',
        success: response.status === 200 && response.data.success,
        statusCode: response.status,
        duration,
        message: `${response.data.total_lines} lignes, ${response.data.columns.length} colonnes`,
        data: {
          total_lines: response.data.total_lines,
          columns: response.data.columns.slice(0, 5)
        }
      });
    } catch (error: any) {
      this.results.push({
        route: '/api/get-data',
        method: 'GET',
        success: false,
        statusCode: error.response?.status || 0,
        duration: 0,
        message: 'Échec de récupération des données',
        error: error.response?.data?.error || error.message
      });
    }
  }

  /**
   * Test 4: POST /api/process-celldown
   */
  private async testProcessCelldown(): Promise<void> {
    try {
      const { result: response, duration } = await measureTime(() =>
        this.client.processCelldown(this.targetCelldownPath, {
          date_str: '13062026', // Format jjmmaaaa
          reference_name: 'TestCellDown',
          colown_key_path_source: 'Codesite',
          target_key_column: 'Site Code,SITE_CODE,site code,Code Site',
          target_value_column: 'Comment,COMMENT,comment',
          source_sheet_path: 'Sheet1'
        })
      );

      this.results.push({
        route: '/api/process-celldown',
        method: 'POST',
        success: response.status === 200 && response.data.success,
        statusCode: response.status,
        duration,
        message: response.data.message,
        data: {
          filename: response.data.filename,
          lines: response.data.lines,
          columns: response.data.columns?.length
        }
      });
    } catch (error: any) {
      this.results.push({
        route: '/api/process-celldown',
        method: 'POST',
        success: false,
        statusCode: error.response?.status || 0,
        duration: 0,
        message: 'Échec du process celldown',
        error: error.response?.data?.error || error.message
      });
    }
  }

  /**
   * Test 5: POST /api/process-xlookup
   */
  private async testProcessXlookup(): Promise<void> {
    try {
      const { result: response, duration } = await measureTime(() =>
        this.client.processXlookup(this.targetXlookupPath, {
          source_key_column: 'Codesite',
          target_key_column: 'Site ID,SITE_ID,site id',
          target_value_column: 'Actions en cours,Actions',
          source_sheet_name: 'Sheet1'
        })
      );

      this.results.push({
        route: '/api/process-xlookup',
        method: 'POST',
        success: response.status === 200 && response.data.success,
        statusCode: response.status,
        duration,
        message: response.data.message,
        data: {
          filename: response.data.filename,
          lines: response.data.lines,
          columns: response.data.columns?.length
        }
      });
    } catch (error: any) {
      this.results.push({
        route: '/api/process-xlookup',
        method: 'POST',
        success: false,
        statusCode: error.response?.status || 0,
        duration: 0,
        message: 'Échec du process xlookup',
        error: error.response?.data?.error || error.message
      });
    }
  }

  /**
   * Test 6: POST /api/process-ticket
   */
  private async testProcessTicket(): Promise<void> {
    try {
      const { result: response, duration } = await measureTime(() =>
        this.client.processTicket(this.targetTicketPath, {
          reference_name: 'TestTicket',
          source_key_column: 'Codesite',
          source_sheet_name: 'Sheet1',
          result_column_name: 'Ticket',
          target_join_columns: JSON.stringify([
            ['Ticket ID'],
            ['Description'],
            ['Solution']
          ]),
          join_separator: '..',
          ignore_empty: 'true'
        })
      );

      this.results.push({
        route: '/api/process-ticket',
        method: 'POST',
        success: response.status === 200 && response.data.success,
        statusCode: response.status,
        duration,
        message: response.data.message,
        data: {
          filename: response.data.filename,
          lines: response.data.lines,
          columns: response.data.columns?.length
        }
      });
    } catch (error: any) {
      this.results.push({
        route: '/api/process-ticket',
        method: 'POST',
        success: false,
        statusCode: error.response?.status || 0,
        duration: 0,
        message: 'Échec du process ticket',
        error: error.response?.data?.error || error.message
      });
    }
  }

  /**
   * Test 7: GET /api/export
   */
  private async testExport(): Promise<void> {
    try {
      const { result: response, duration } = await measureTime(() =>
        this.client.export()
      );

      const fileSize = response.data.byteLength;

      this.results.push({
        route: '/api/export',
        method: 'GET',
        success: response.status === 200 && fileSize > 0,
        statusCode: response.status,
        duration,
        message: `Fichier exporté (${fileSize} bytes)`,
        data: { size: fileSize }
      });
    } catch (error: any) {
      this.results.push({
        route: '/api/export',
        method: 'GET',
        success: false,
        statusCode: error.response?.status || 0,
        duration: 0,
        message: 'Échec de l\'export',
        error: error.response?.data?.error || error.message
      });
    }
  }

  /**
   * Test 8: DELETE /api/clear-main-file
   */
  private async testClearMainFile(): Promise<void> {
    try {
      const { result: response, duration } = await measureTime(() =>
        this.client.clearMainFile()
      );

      this.results.push({
        route: '/api/clear-main-file',
        method: 'DELETE',
        success: response.status === 200 && response.data.success,
        statusCode: response.status,
        duration,
        message: response.data.message,
        data: response.data
      });
    } catch (error: any) {
      this.results.push({
        route: '/api/clear-main-file',
        method: 'DELETE',
        success: false,
        statusCode: error.response?.status || 0,
        duration: 0,
        message: 'Échec du clear',
        error: error.response?.data?.error || error.message
      });
    }
  }

  /**
   * Exécute tous les tests
   */
  async runAllTests(): Promise<void> {
    displaySectionHeader('TESTS DES ROUTES API BACKEND');

    // Vérification des prérequis
    if (!this.checkPrerequisites()) {
      return;
    }

    // Test 1: Health check
    console.log('\n📋 Test 1/8: Health check...');
    await this.testHealth();
    displayTestResult(this.results[this.results.length - 1]);

    // Vérifier si le serveur est accessible
    if (!this.results[0].success) {
      console.log('\n⚠️  Le serveur n\'est pas accessible. Arrêt des tests.');
      console.log('   Démarrez le serveur avec: python app.py');
      return;
    }

    // Test 2: Upload main file
    console.log('\n📋 Test 2/8: Upload main file...');
    await this.testUploadMainFile();
    displayTestResult(this.results[this.results.length - 1]);

    // Pause pour laisser le serveur traiter
    await sleep(1000);

    // Test 3: Get data
    console.log('\n📋 Test 3/8: Get data...');
    await this.testGetData();
    displayTestResult(this.results[this.results.length - 1]);

    // Test 4: Process celldown
    console.log('\n📋 Test 4/8: Process celldown...');
    await this.testProcessCelldown();
    displayTestResult(this.results[this.results.length - 1]);

    await sleep(1000);

    // Test 5: Process xlookup
    console.log('\n📋 Test 5/8: Process xlookup...');
    await this.testProcessXlookup();
    displayTestResult(this.results[this.results.length - 1]);

    await sleep(1000);

    // Test 6: Process ticket
    console.log('\n📋 Test 6/8: Process ticket...');
    await this.testProcessTicket();
    displayTestResult(this.results[this.results.length - 1]);

    await sleep(1000);

    // Test 7: Export
    console.log('\n📋 Test 7/8: Export file...');
    await this.testExport();
    displayTestResult(this.results[this.results.length - 1]);

    // Test 8: Clear main file
    console.log('\n📋 Test 8/8: Clear main file...');
    await this.testClearMainFile();
    displayTestResult(this.results[this.results.length - 1]);

    // Afficher le résumé
    displaySummary(this.results);
  }
}

// Exécuter les tests
const tester = new ApiTester();
tester.runAllTests().catch(console.error);
