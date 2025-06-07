import { useState, useCallback } from 'react';
import WebApp from '@twa-dev/sdk';

interface FileWithPreview extends File {
  preview?: string;
}

const API_URL = process.env.NODE_ENV === 'production' 
  ? 'https://api.eonae.dev' 
  : 'http://localhost:8000';

export const FileUpload = () => {
  const [files, setFiles] = useState<FileWithPreview[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const droppedFiles = Array
      .from(e.dataTransfer.files)
      .filter(file => file.type.startsWith('audio/'));
  
    if (droppedFiles.length === 0) {
      setError('Пожалуйста, загрузите только аудио-файлы');
      return;
    }
    setFiles(prev => [...prev, ...droppedFiles]);
    setError(null);
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files).filter(file => file.type.startsWith('audio/'));
      if (selectedFiles.length === 0) {
        setError('Пожалуйста, выберите только аудио-файлы');
        return;
      }
      setFiles(prev => [...prev, ...selectedFiles]);
      setError(null);
    }
  }, []);

  const handleRemoveFile = useCallback((index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
    setError(null);
  }, []);

  const handleUpload = useCallback(async () => {
    if (files.length === 0) return;

    setIsUploading(true);
    setError(null);

    try {
      for (const file of files) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_URL}/upload`, {
          method: 'POST',
          body: formData,
          headers: {
            'X-User-ID': WebApp.initDataUnsafe.user?.id.toString() || '',
          },
        });

        if (!response.ok) {
          throw new Error(`Ошибка загрузки: ${response.statusText}`);
        }
      }

      // Очищаем список файлов после успешной загрузки
      setFiles([]);
      WebApp.showAlert('Файлы успешно загружены!');
    } catch (error) {
      console.error('Error uploading file:', error);
      setError(error instanceof Error ? error.message : 'Произошла ошибка при загрузке файлов');
    } finally {
      setIsUploading(false);
    }
  }, [files]);

  return (
    <div className="file-upload">
      <h2>Загрузка файлов</h2>
      
      <div
        className={`drop-zone ${isDragging ? 'active' : ''}`}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={() => document.getElementById('file-input')?.click()}
      >
        <p>Перетащите аудиофайлы сюда или нажмите для выбора</p>
        <input
          id="file-input"
          type="file"
          className="file-input"
          onChange={handleFileSelect}
          multiple
          accept="audio/*"
        />
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {files.length > 0 && (
        <div className="file-list">
          {files.map((file, index) => (
            <div key={index} className="file-item">
              <span className="file-name">{file.name}</span>
              <span
                className="file-remove"
                onClick={() => handleRemoveFile(index)}
              >
                ✕
              </span>
            </div>
          ))}
        </div>
      )}

      <button
        className="upload-button"
        onClick={handleUpload}
        disabled={files.length === 0 || isUploading}
      >
        {isUploading ? 'Загрузка...' : 'Загрузить'}
      </button>
    </div>
  );
}; 