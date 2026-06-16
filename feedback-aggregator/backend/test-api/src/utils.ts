import * as fs from 'fs';
import * as path from 'path';
import { TestResult } from './types';

/**
 * Couleurs pour l'affichage console
 */
export const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  gray: '\x1b[90m'
};

/**
 * Affiche un résultat de test formaté
 */
export function displayTestResult(result: TestResult): void {
  const icon = result.success ? '✅' : '❌';
  const color = result.success ? colors.green : colors.red;
  
  console.log(`\n${icon} ${color}${result.method} ${result.route}${colors.reset}`);
  console.log(`   Status: ${result.statusCode}`);
  console.log(`   Duration: ${result.duration}ms`);
  console.log(`   Message: ${result.message}`);
  
  if (result.error) {
    console.log(`   ${colors.red}Error: ${result.error}${colors.reset}`);
  }
  
  if (result.data && Object.keys(result.data).length > 0) {
    console.log(`   ${colors.gray}Data:${colors.reset}`, JSON.stringify(result.data, null, 2));
  }
}

/**
 * Affiche un en-tête de section
 */
export function displaySectionHeader(title: string): void {
  console.log(`\n${colors.cyan}${'='.repeat(60)}${colors.reset}`);
  console.log(`${colors.cyan}${title}${colors.reset}`);
  console.log(`${colors.cyan}${'='.repeat(60)}${colors.reset}`);
}

/**
 * Affiche un résumé des tests
 */
export function displaySummary(results: TestResult[]): void {
  const total = results.length;
  const passed = results.filter(r => r.success).length;
  const failed = total - passed;
  const totalDuration = results.reduce((sum, r) => sum + r.duration, 0);
  
  displaySectionHeader('RÉSUMÉ DES TESTS');
  
  console.log(`\nTotal: ${total} tests`);
  console.log(`${colors.green}✅ Réussis: ${passed}${colors.reset}`);
  console.log(`${colors.red}❌ Échoués: ${failed}${colors.reset}`);
  console.log(`⏱️  Durée totale: ${totalDuration}ms`);
  
  if (failed === 0) {
    console.log(`\n${colors.green}🎉 TOUS LES TESTS SONT PASSÉS !${colors.reset}`);
  } else {
    console.log(`\n${colors.red}⚠️  CERTAINS TESTS ONT ÉCHOUÉ${colors.reset}`);
  }
  
  console.log(`${colors.cyan}${'='.repeat(60)}${colors.reset}\n`);
}

/**
 * Vérifie si un fichier existe
 */
export function fileExists(filePath: string): boolean {
  return fs.existsSync(filePath);
}

/**
 * Lit un fichier
 */
export function readFile(filePath: string): Buffer {
  return fs.readFileSync(filePath);
}

/**
 * Liste les fichiers d'un répertoire
 */
export function listFiles(dirPath: string, extension?: string): string[] {
  if (!fs.existsSync(dirPath)) {
    return [];
  }
  
  const files = fs.readdirSync(dirPath);
  
  if (extension) {
    return files.filter(f => f.endsWith(extension));
  }
  
  return files;
}

/**
 * Attend un certain temps (en ms)
 */
export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Mesure le temps d'exécution d'une fonction
 */
export async function measureTime<T>(fn: () => Promise<T>): Promise<{ result: T; duration: number }> {
  const start = Date.now();
  const result = await fn();
  const duration = Date.now() - start;
  return { result, duration };
}
