/**
 * Exemples d'utilisation du client API TypeScript
 */

import { ApiClient } from './api-client';
import * as path from 'path';

async function examples() {
  const client = new ApiClient('http://localhost:5000');
  
  // ============================================================
  // Exemple 1: Vérifier la santé du serveur
  // ============================================================
  console.log('1. Health check...');
  try {
    const response = await client.health();
    console.log('✅ Serveur actif:', response.data.message);
  } catch (error) {
    console.error('❌ Serveur inaccessible');
  }

  // ============================================================
  // Exemple 2: Upload d'un fichier principal
  // ============================================================
  console.log('\n2. Upload fichier principal...');
  const mainFile = path.join(__dirname, '../../test_files/main_test.xlsx');
  try {
    const response = await client.uploadMainFile(mainFile, 'Sheet1');
    console.log('✅ Upload réussi:');
    console.log(`   - Fichier: ${response.data.filename}`);
    console.log(`   - Lignes: ${response.data.lines}`);
    console.log(`   - Taille: ${response.data.size} bytes`);
  } catch (error: any) {
    console.error('❌ Upload échoué:', error.response?.data?.error);
  }

  // ============================================================
  // Exemple 3: Récupérer les données paginées
  // ============================================================
  console.log('\n3. Récupération des données...');
  try {
    const response = await client.getData({
      sheet: 'Sheet1',  // ou 0 pour la première feuille
      limit: 50,         // nombre max de lignes
      offset: 0          // à partir de la ligne 0
    });
    console.log('✅ Données récupérées:');
    console.log(`   - Total lignes: ${response.data.total_lines}`);
    console.log(`   - Colonnes: ${response.data.columns.join(', ')}`);
    console.log(`   - Données renvoyées: ${response.data.data.length} lignes`);
  } catch (error: any) {
    console.error('❌ Échec:', error.response?.data?.error);
  }

  // ============================================================
  // Exemple 4: Process CellDown
  // ============================================================
  console.log('\n4. Process CellDown...');
  const targetCellDown = path.join(__dirname, '../../test_files/target_ticket.xlsx');
  try {
    const response = await client.processCelldown(targetCellDown, {
      date_str: '13062026',  // REQUIS: format jjmmaaaa
      reference_name: 'CellDown Test',
      colown_key_path_source: 'Codesite',
      target_key_column: 'Site Code,SITE_CODE',
      target_value_column: 'Comment,COMMENT',
      source_sheet_path: 'Sheet1'
    });
    console.log('✅ CellDown réussi:');
    console.log(`   - Message: ${response.data.message}`);
    console.log(`   - Lignes traitées: ${response.data.lines}`);
  } catch (error: any) {
    console.error('❌ Échec:', error.response?.data?.error);
  }

  // ============================================================
  // Exemple 5: Process XLookup
  // ============================================================
  console.log('\n5. Process XLookup...');
  const targetXLookup = path.join(__dirname, '../../test_files/target_xlookup.xlsx');
  try {
    const response = await client.processXlookup(targetXLookup, {
      source_key_column: 'Codesite',
      target_key_column: 'Site ID,SITE_ID',
      target_value_column: 'Actions en cours,Actions',
      result_column_name: 'Actions',  // nom de la colonne résultat
      reference_name: 'XLookup Test'
    });
    console.log('✅ XLookup réussi:');
    console.log(`   - Message: ${response.data.message}`);
    console.log(`   - Lignes traitées: ${response.data.lines}`);
  } catch (error: any) {
    console.error('❌ Échec:', error.response?.data?.error);
  }

  // ============================================================
  // Exemple 6: Process Ticket
  // ============================================================
  console.log('\n6. Process Ticket...');
  const targetTicket = path.join(__dirname, '../../test_files/target_ticket.xlsx');
  try {
    const response = await client.processTicket(targetTicket, {
      reference_name: 'Ticket',
      source_key_column: 'Codesite',
      result_column_name: 'Ticket Info',
      target_join_columns: JSON.stringify([
        ['Ticket ID'],
        ['Description'],
        ['Solution']
      ]),
      join_separator: ' | ',
      ignore_empty: 'true'
    });
    console.log('✅ Ticket réussi:');
    console.log(`   - Message: ${response.data.message}`);
    console.log(`   - Lignes traitées: ${response.data.lines}`);
  } catch (error: any) {
    console.error('❌ Échec:', error.response?.data?.error);
  }

  // ============================================================
  // Exemple 7: Export du fichier
  // ============================================================
  console.log('\n7. Export du fichier...');
  try {
    const response = await client.export();
    const fileSize = response.data.byteLength;
    console.log('✅ Export réussi:');
    console.log(`   - Taille: ${fileSize} bytes`);
    
    // Optionnel: sauvegarder le fichier
    // const fs = require('fs');
    // fs.writeFileSync('export.xlsx', response.data);
  } catch (error: any) {
    console.error('❌ Échec:', error.response?.data?.error);
  }

  // ============================================================
  // Exemple 8: Nettoyer (clear main file)
  // ============================================================
  console.log('\n8. Nettoyage...');
  try {
    const response = await client.clearMainFile();
    console.log('✅ Nettoyage réussi:', response.data.message);
  } catch (error: any) {
    console.error('❌ Échec:', error.response?.data?.error);
  }

  console.log('\n✨ Tous les exemples terminés !');
}

// ============================================================
// Exemple d'utilisation avec gestion d'erreurs complète
// ============================================================
async function advancedExample() {
  const client = new ApiClient();
  
  try {
    // 1. Vérifier le serveur
    await client.health();
    
    // 2. Upload
    const mainFile = 'chemin/vers/fichier.xlsx';
    const uploadResponse = await client.uploadMainFile(mainFile);
    console.log(`Fichier uploadé: ${uploadResponse.data.filename}`);
    
    // 3. Process
    const targetFile = 'chemin/vers/target.xlsx';
    const processResponse = await client.processXlookup(targetFile, {
      source_key_column: 'ID',
      target_key_column: 'Site ID',
      target_value_column: 'Status'
    });
    console.log(`Process terminé: ${processResponse.data.lines} lignes`);
    
    // 4. Récupérer les données
    const dataResponse = await client.getData({ limit: 100 });
    console.log(`Colonnes: ${dataResponse.data.columns.join(', ')}`);
    
    // 5. Export
    const exportResponse = await client.export();
    console.log(`Fichier exporté: ${exportResponse.data.byteLength} bytes`);
    
  } catch (error: any) {
    if (error.response) {
      // Erreur HTTP du serveur
      console.error('Erreur serveur:', error.response.status);
      console.error('Message:', error.response.data?.error);
    } else if (error.request) {
      // Pas de réponse du serveur
      console.error('Serveur non accessible');
    } else {
      // Autre erreur
      console.error('Erreur:', error.message);
    }
  }
}

// Exécuter les exemples si appelé directement
if (require.main === module) {
  examples().catch(console.error);
  // ou: advancedExample().catch(console.error);
}

export { examples, advancedExample };
