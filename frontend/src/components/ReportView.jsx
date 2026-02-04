import React from 'react';
import { CheckCircle, AlertCircle, FileText } from 'lucide-react';

export default function ReportView({ report }) {
    if (!report) return null;

    return (
        <div className="animate-fade-in" style={{ marginTop: '2rem' }}>
            <h2 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <FileText color="var(--accent-color)" />
                Evaluation Report
            </h2>

            <div className="glass-panel" style={{ padding: '2rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2rem', borderBottom: '1px solid var(--glass-border)', paddingBottom: '1rem' }}>
                    <div>
                        <span style={{ color: 'var(--text-secondary)' }}>Total Questions</span>
                        <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{report.total_questions || 0}</div>
                    </div>
                    <div>
                        <span style={{ color: 'var(--text-secondary)' }}>Total Score</span>
                        <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--accent-color)' }}>
                            {report.total_marks_awarded} / {report.total_max_marks}
                        </div>
                    </div>
                    <div>
                        <span style={{ color: 'var(--text-secondary)' }}>Percentage</span>
                        <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{report.percentage}%</div>
                    </div>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                    {report.results.map((item, index) => (
                        <div key={index} style={{
                            background: 'rgba(255,255,255,0.03)',
                            borderRadius: '0.5rem',
                            padding: '1.5rem',
                            borderLeft: `4px solid ${item.marks_awarded > 0 ? 'var(--success)' : 'var(--danger)'}`
                        }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                                <h4 style={{ color: 'var(--text-primary)' }}>Q{item.question_number}: {item.question_text || 'Unidentified Question'}</h4>
                                <span style={{
                                    background: item.marks_awarded > 0 ? 'rgba(74, 222, 128, 0.2)' : 'rgba(248, 113, 113, 0.2)',
                                    color: item.marks_awarded > 0 ? 'var(--success)' : 'var(--danger)',
                                    padding: '0.25rem 0.75rem',
                                    borderRadius: '1rem',
                                    fontSize: '0.9rem',
                                    fontWeight: 'bold'
                                }}>
                                    {item.marks_awarded} / {item.max_marks}
                                </span>
                            </div>

                            <div style={{ marginBottom: '1rem' }}>
                                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>STUDENT ANSWER</div>
                                <div style={{ padding: '0.75rem', background: 'rgba(0,0,0,0.3)', borderRadius: '0.25rem', fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}>
                                    {item.student_answer}
                                </div>
                            </div>

                            <div>
                                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>FEEDBACK</div>
                                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'start' }}>
                                    {item.marks_awarded >= item.max_marks ? <CheckCircle size={18} color="var(--success)" /> : <AlertCircle size={18} color="var(--danger)" />}
                                    <p style={{ lineHeight: '1.4' }}>{item.feedback}</p>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
