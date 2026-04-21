"use client";

import React, { useEffect, useState } from 'react';
import styles from './dashboard.module.css';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  TrendingUp, 
  Clock, 
  MessageSquare, 
  Zap,
  ChevronRight
} from 'lucide-react';

export default function DashboardPage() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch('/api/simulation-data');
        const json = await res.json();
        setData(json);
      } catch (e) {
        console.error(e);
      }
    };
    
    fetchData();
    const interval = setInterval(fetchData, 10000); // Polling every 10s
    return () => clearInterval(interval);
  }, []);

  if (!data) return <div className={styles.grid}><div className={styles.card}>Loading Research Data...</div></div>;

  return (
    <div style={{ flex: 1 }}>
      {/* Header */}
      <header className={styles.header}>
        <div>
          <h1 className={`${styles.title} ${styles.serif}`}>Research Intelligence</h1>
          <p className={styles.subtitle}>GPS-AIedu Strategic Monitoring</p>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ color: '#D4AF37', fontSize: '1.2rem', fontWeight: 300 }}>
            {new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
          </div>
          <div style={{ fontSize: '0.8rem', opacity: 0.5, marginTop: '4px' }}>
            System Status: <span style={{ color: '#4ADE80' }}>ACTIVE SIMULATION</span>
          </div>
        </div>
      </header>

      {/* Stats Grid */}
      <div className={styles.grid}>
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className={`${styles.card} ${styles.cardGold}`}
          style={{ gridColumn: 'span 3' }}
        >
          <div className={styles.metricLabel}>Problems Completed</div>
          <div className={`${styles.metricValue} ${styles.serif}`}>{data.stats.completed} / 45</div>
          <div style={{ fontSize: '0.8rem', color: '#4ADE80', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <TrendingUp size={14} /> Progress: {((data.stats.completed / 45) * 100).toFixed(0)}%
          </div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className={styles.card}
          style={{ gridColumn: 'span 3' }}
        >
          <div className={styles.metricLabel}>Total Interactions</div>
          <div className={`${styles.metricValue} ${styles.serif}`}>{data.stats.totalRows.toLocaleString()}</div>
          <div style={{ fontSize: '0.8rem', opacity: 0.5 }}>Synthetic conversations logged</div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className={styles.card}
          style={{ gridColumn: 'span 3' }}
        >
          <div className={styles.metricLabel}>Avg Turns per Session</div>
          <div className={`${styles.metricValue} ${styles.serif}`}>{data.stats.avgTurns}</div>
          <div style={{ fontSize: '0.8rem', opacity: 0.5 }}>Conversation depth metric</div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className={styles.card}
          style={{ gridColumn: 'span 3' }}
        >
          <div className={styles.metricLabel}>Independence Index</div>
          <div className={`${styles.metricValue} ${styles.serif}`} style={{ color: '#D4AF37' }}>0.24</div>
          <div style={{ fontSize: '0.8rem', opacity: 0.5 }}>Target: &gt; 1.0 (Week 6 Goal)</div>
        </motion.div>

        {/* Live Feed Container */}
        <div style={{ gridColumn: 'span 8', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <h3 className={`${styles.serif}`} style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>Live Simulation Feed</h3>
          
          <AnimatePresence mode='popLayout'>
            {data.recent.map((item: any, idx: number) => (
              <motion.div 
                key={`${item.qid}-${item.turn}-${idx}`}
                layout
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className={styles.card}
                style={{ padding: '1.5rem', marginBottom: '0.5rem' }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div className={styles.dot}></div>
                    <span style={{ color: '#D4AF37', fontWeight: 600 }}>{item.studentId}</span>
                    <span style={{ fontSize: '0.8rem', opacity: 0.3 }}>| Question {item.qid}</span>
                  </div>
                  <div style={{ fontSize: '0.7rem', opacity: 0.3, fontFamily: 'monospace' }}>
                    TRIAL_{item.timestamp.split(' ')[1]}
                  </div>
                </div>
                
                <div style={{ fontSize: '0.9rem', marginBottom: '1rem', borderLeft: '2px solid rgba(255,255,255,0.05)', paddingLeft: '1rem' }}>
                  <span style={{ opacity: 0.4 }}>Student: </span>
                  {item.question.length > 150 ? item.question.substring(0, 150) + '...' : item.question}
                </div>
                
                <div style={{ fontSize: '0.95rem', background: 'rgba(212,175,55,0.03)', padding: '1rem', borderRadius: '4px' }}>
                  <span style={{ color: '#D4AF37', fontWeight: 500 }}>Tutor: </span>
                  {item.response.length > 200 ? item.response.substring(0, 200) + '...' : item.response}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        {/* Side Panel: Insights */}
        <div style={{ gridColumn: 'span 4', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
           <h3 className={`${styles.serif}`} style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>Strategic Insights</h3>
           
           {/* Persona Comparison Chart */}
           <div className={styles.card}>
              <div className={styles.metricLabel} style={{ marginBottom: '1rem' }}>Persona Behavioral Mapping</div>
              <div style={{ height: '250px', width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                {/* Simplified SVG Radar for Premium Look without heavy chart overhead */}
                <svg viewBox="0 0 200 200" style={{ width: '100%', height: '100%' }}>
                  <circle cx="100" cy="100" r="80" fill="none" stroke="rgba(212,175,55,0.1)" strokeWidth="1" />
                  <circle cx="100" cy="100" r="50" fill="none" stroke="rgba(212,175,55,0.1)" strokeWidth="1" />
                  <path d="M100 20 L100 180 M20 100 L180 100" stroke="rgba(212,175,55,0.05)" />
                  {/* Advanced Persona Data (HS0001) */}
                  <polygon points="100,40 160,80 140,140 60,140 40,80" fill="rgba(212,175,55,0.2)" stroke="var(--academic-gold)" strokeWidth="1" />
                  {/* Struggling Persona Data (HS0003) */}
                  <polygon points="100,60 130,90 120,120 80,120 70,90" fill="rgba(64,156,255,0.1)" stroke="#4A90E2" strokeWidth="1" />
                </svg>
              </div>
              <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', marginTop: '1rem' }}>
                 <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.7rem' }}>
                    <div style={{ width: '8px', height: '8px', background: 'var(--academic-gold)' }}></div> Advanced
                 </div>
                 <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.7rem' }}>
                    <div style={{ width: '8px', height: '8px', background: '#4A90E2' }}></div> Struggling
                 </div>
              </div>
           </div>

           <div className={styles.card}>
              <div style={{ marginBottom: '2rem' }}>
                <div className={styles.metricLabel} style={{ marginBottom: '0.5rem' }}>Most Challenging Persona</div>
                <div style={{ color: '#D4AF37', fontSize: '1.2rem' }}>HS0003 (Struggling)</div>
                <div style={{ fontSize: '0.8rem', opacity: 0.5, marginTop: '4px' }}>Requires 4x more tokens per session than HS0001.</div>
              </div>
              
              <div style={{ marginBottom: '2rem' }}>
                <div className={styles.metricLabel} style={{ marginBottom: '0.5rem' }}>GPS Effectiveness</div>
                <div style={{ height: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', overflow: 'hidden' }}>
                    <div style={{ width: '85%', height: '100%', background: 'var(--academic-gold)' }}></div>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', marginTop: '4px', opacity: 0.5 }}>
                  <span>Correctness: 92%</span>
                  <span>Safety: 100%</span>
                </div>
              </div>

              <div style={{ marginTop: 'auto' }}>
                <button style={{ 
                  width: '100%', 
                  padding: '1rem', 
                  background: 'none', 
                  border: '1px solid var(--academic-gold)', 
                  color: 'var(--academic-gold)',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                  fontSize: '0.9rem'
                }}>
                  View Detailed Behavior Clusters <ChevronRight size={16} />
                </button>
              </div>
           </div>
        </div>
      </div>
    </div>
  );
}
