// components/ConfigPanel.jsx
import React from 'react';
import PropTypes from 'prop-types';
import { ConfigForm } from './ConfigForm';
import { DataTable } from './Database';

export function ConfigPanel({
  selectedFile,
  files,
  config,
  onConfigChange,
  columns,
  sheets,
  onFileSelect,
  onSubmit,
  submitting,
}) {
  return (
    <div className="w-full md:w-2/3 p-8 bg-white overflow-y-auto">
      <h2 className="text-xl font-semibold text-gray-700 mb-6">
        {selectedFile ? selectedFile.name : 'Aucun fichier sélectionné'}
      </h2>

      <ConfigForm
        files={files}
        selectedFile={selectedFile}
        config={config}
        onConfigChange={onConfigChange}
        columns={columns}
        sheets={sheets}
        onFileSelect={onFileSelect}
      />

      <DataTable />

      <button
        onClick={onSubmit}
        disabled={submitting}
        className="w-full bg-[#f97316] hover:bg-[#ea580c] text-white font-medium py-3 rounded-md text-lg transition-colors disabled:bg-orange-300 disabled:cursor-not-allowed"
      >
        {submitting ? 'Compilation en cours...' : 'Lancer la compilation'}
      </button>
    </div>
  );
}

ConfigPanel.propTypes = {
  selectedFile: PropTypes.object,
  files: PropTypes.array.isRequired,
  config: PropTypes.object.isRequired,
  onConfigChange: PropTypes.func.isRequired,
  columns: PropTypes.array.isRequired,
  sheets: PropTypes.array.isRequired,
  onFileSelect: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
  submitting: PropTypes.bool,
};