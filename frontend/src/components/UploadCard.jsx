import React, { useRef, useState } from 'react';
import { Upload, FileText, CheckCircle, X } from 'lucide-react';

export default function UploadCard({ title, accept, onFileSelect, onTextChange, textValue, textPlaceholder, type }) {
    const fileInputRef = useRef(null);
    const [fileName, setFileName] = useState(null);

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            setFileName(file.name);
            onFileSelect(file);
        }
    };

    const clearFile = () => {
        setFileName(null);
        onFileSelect(null);
        if (fileInputRef.current) fileInputRef.current.value = '';
    };

    return (
        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                <FileText size={20} color="var(--accent-color)" />
                <h3>{title}</h3>
            </div>

            <div
                style={{
                    border: '2px dashed var(--glass-border)',
                    borderRadius: '0.5rem',
                    padding: '2rem',
                    textAlign: 'center',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    backgroundColor: 'rgba(0,0,0,0.2)'
                }}
                onClick={() => fileInputRef.current.click()}
                onDragOver={(e) => e.preventDefault()}
                onDrop={(e) => {
                    e.preventDefault();
                    const file = e.dataTransfer.files[0];
                    if (file) {
                        setFileName(file.name);
                        onFileSelect(file);
                    }
                }}
            >
                <input
                    type="file"
                    ref={fileInputRef}
                    style={{ display: 'none' }}
                    accept={accept}
                    onChange={handleFileChange}
                />

                {fileName ? (
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', color: 'var(--success)' }}>
                        <CheckCircle size={20} />
                        <span>{fileName}</span>
                        <button
                            onClick={(e) => { e.stopPropagation(); clearFile(); }}
                            style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', marginLeft: '0.5rem' }}
                        >
                            <X size={16} />
                        </button>
                    </div>
                ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)' }}>
                        <Upload size={24} />
                        <span>Click or Drag to Upload</span>
                    </div>
                )}
            </div>

            {onTextChange && (
                <>
                    <div style={{ textAlign: 'center', color: 'var(--text-secondary)', fontSize: '0.8rem' }}>OR</div>
                    <textarea
                        className="glass-panel"
                        style={{
                            width: '100%',
                            minHeight: '100px',
                            background: 'rgba(0,0,0,0.3)',
                            color: 'var(--text-primary)',
                            padding: '0.75rem',
                            resize: 'vertical',
                            border: '1px solid var(--glass-border)',
                            fontFamily: 'monospace'
                        }}
                        placeholder={textPlaceholder}
                        value={textValue}
                        onChange={(e) => onTextChange(e.target.value)}
                    />
                </>
            )}
        </div>
    );
}
